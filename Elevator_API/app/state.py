"""Shared state management for the elevator system.

Replaces Rust's Arc<RwLock<T>> with Python asyncio.Lock.
"""
import asyncio
from typing import Dict, Set, Optional
from uuid import UUID
from datetime import datetime
from sortedcontainers import SortedSet

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .models import (
    ClientInfo,
    FloorRequest,
    ElevatorState,
    Direction,
    FloorRequestUpdate,
)
from .algorithm import calculate_next_floor
from .rl_router import calculate_next_floor_rl, load_model as _load_rl_model

# Attempt to load the latest PPO checkpoint at startup
_MODEL_PATH = Path(__file__).parent.parent / "models" / "ppo_checkpoint_ep1688.zip"
_rl_available = _load_rl_model(_MODEL_PATH)
_rl_executor = ThreadPoolExecutor(max_workers=1)


class ElevatorSystemState:
    """Centralized state manager for the elevator system.

    Manages:
    - Client sessions
    - Floor requests (priority-sorted)
    - Elevator state (position, direction, operator)
    - Subscription broadcasting
    """

    def __init__(self):
        """Initialize the state manager."""
        # Client sessions
        self.clients: Dict[UUID, ClientInfo] = {}
        self.clients_lock = asyncio.Lock()

        # Floor requests (sorted by priority)
        self.floor_requests: Set[FloorRequest] = set()
        self.requests_lock = asyncio.Lock()

        # Elevator state
        self.elevator_state = ElevatorState()
        self.elevator_lock = asyncio.Lock()

        # Subscription queue for GraphQL real-time updates
        self.subscribers: list[asyncio.Queue] = []
        self.subscribers_lock = asyncio.Lock()

    async def add_client(self, client: ClientInfo) -> None:
        """Register a new client."""
        async with self.clients_lock:
            self.clients[client.id] = client

    async def remove_client(self, client_id: UUID) -> None:
        """Remove a client session."""
        async with self.clients_lock:
            self.clients.pop(client_id, None)

    async def get_client(self, client_id: UUID) -> Optional[ClientInfo]:
        """Get client information."""
        async with self.clients_lock:
            return self.clients.get(client_id)

    async def update_client_poll_time(self, client_id: UUID) -> None:
        """Update client's last poll timestamp."""
        async with self.clients_lock:
            if client_id in self.clients:
                self.clients[client_id].last_poll = datetime.utcnow()

    async def add_floor_request(self, request: FloorRequest) -> None:
        """Add a floor request to the queue."""
        async with self.requests_lock:
            self.floor_requests.add(request)

        # Notify all subscribers of the state change
        await self.broadcast_update()

    async def remove_floor_request(self, request_id: UUID) -> bool:
        """Remove a floor request by ID.

        Returns:
            True if request was found and removed, False otherwise.
        """
        found = False
        async with self.requests_lock:
            request_to_remove = next(
                (req for req in self.floor_requests if req.id == request_id),
                None
            )
            if request_to_remove:
                self.floor_requests.discard(request_to_remove)
                found = True
        if found:
            await self.broadcast_update()
        return found

    async def get_floor_requests(self) -> list[FloorRequest]:
        """Get all floor requests, sorted by priority."""
        async with self.requests_lock:
            # Sort by the FloorRequest ordering (priority, then timestamp)
            return sorted(self.floor_requests)

    async def get_elevator_state(self) -> ElevatorState:
        """Get current elevator state."""
        async with self.elevator_lock:
            return self.elevator_state.model_copy()

    async def update_elevator_floor(self, floor: int) -> None:
        """Update elevator's current floor."""
        async with self.elevator_lock:
            self.elevator_state.current_floor = floor

        # Notify all subscribers of the state change
        await self.broadcast_update()

    async def update_elevator_direction(self, direction: Direction) -> None:
        """Update elevator's direction."""
        async with self.elevator_lock:
            self.elevator_state.direction = direction

        # Notify all subscribers of the state change
        await self.broadcast_update()

    async def set_operator(self, operator_id: Optional[UUID]) -> None:
        """Set or clear the current operator."""
        async with self.elevator_lock:
            self.elevator_state.operator_id = operator_id

        # Notify all subscribers of the state change
        await self.broadcast_update()

    async def calculate_next_floor(self) -> tuple[Optional[int], Direction]:
        """Calculate the next floor, using RL when available, SCAN as fallback.

        Returns:
            Tuple of (next_floor, direction)
        """
        async with self.elevator_lock, self.requests_lock:
            current_floor = self.elevator_state.current_floor
            direction = self.elevator_state.direction
            requests = set(self.floor_requests)

        if _rl_available:
            loop = asyncio.get_running_loop()
            try:
                rl_floor, rl_dir = await asyncio.wait_for(
                    loop.run_in_executor(
                        _rl_executor,
                        calculate_next_floor_rl,
                        current_floor,
                        direction,
                        requests,
                    ),
                    timeout=3.0,
                )
                if rl_floor is not None:
                    return rl_floor, rl_dir
            except asyncio.TimeoutError:
                logger.warning("RL prediction timed out — falling back to SCAN")

        return calculate_next_floor(current_floor, direction, requests)

    async def get_state_update(self, use_rl: bool = False) -> FloorRequestUpdate:
        """Get complete state update for polling or subscriptions.

        use_rl=True runs the full RL prediction (for explicit poll requests).
        use_rl=False uses SCAN only (for broadcast, keeps event loop free).
        """
        requests = await self.get_floor_requests()
        elevator_state = await self.get_elevator_state()
        if use_rl:
            next_floor, _ = await self.calculate_next_floor()
        else:
            next_floor, _ = calculate_next_floor(
                elevator_state.current_floor,
                elevator_state.direction,
                set(requests),
            )

        return FloorRequestUpdate(
            requests=requests,
            next_floor=next_floor,
            current_floor=elevator_state.current_floor,
            direction=elevator_state.direction,
        )

    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to state updates.

        Returns:
            Queue that will receive FloorRequestUpdate messages.
        """
        queue = asyncio.Queue(maxsize=100)
        async with self.subscribers_lock:
            self.subscribers.append(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Unsubscribe from state updates."""
        async with self.subscribers_lock:
            if queue in self.subscribers:
                self.subscribers.remove(queue)

    async def broadcast_update(self) -> None:
        """Broadcast current state to all subscribers."""
        update = await self.get_state_update()

        async with self.subscribers_lock:
            # Remove disconnected subscribers
            dead_queues = []
            for queue in self.subscribers:
                try:
                    queue.put_nowait(update)
                except asyncio.QueueFull:
                    # Queue is full, skip this update
                    pass
                except Exception:
                    # Queue is closed or invalid, mark for removal
                    dead_queues.append(queue)

            for queue in dead_queues:
                self.subscribers.remove(queue)


# Global state instance
state = ElevatorSystemState()
