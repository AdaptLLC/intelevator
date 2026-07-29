"""Shared state management for the elevator system."""
import asyncio
import logging
from typing import Dict, Set, Optional
from uuid import UUID, uuid4
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .models import (
    ClientInfo,
    FloorRequest,
    ElevatorState,
    Direction,
    FloorRequestUpdate,
    PassengerRecord,
)
from .algorithm import calculate_next_floor
from .rl_router import calculate_next_floor_rl, load_model as _load_rl_model

logger = logging.getLogger(__name__)

_MODEL_PATH = Path(__file__).parent.parent / "models" / "ppo_checkpoint_ep1688.zip"
_rl_available = _load_rl_model(_MODEL_PATH)
_rl_executor = ThreadPoolExecutor(max_workers=1)


class ElevatorSystemState:
    def __init__(self):
        self.clients: Dict[UUID, ClientInfo] = {}
        self.clients_lock = asyncio.Lock()

        self.floor_requests: Set[FloorRequest] = set()
        self.requests_lock = asyncio.Lock()

        # Boarded passengers: id → PassengerRecord
        self.passengers: Dict[UUID, PassengerRecord] = {}
        self.passengers_lock = asyncio.Lock()

        self.elevator_state = ElevatorState()
        self.elevator_lock = asyncio.Lock()

        self.subscribers: list[asyncio.Queue] = []
        self.subscribers_lock = asyncio.Lock()

    async def add_client(self, client: ClientInfo) -> None:
        async with self.clients_lock:
            self.clients[client.id] = client

    async def remove_client(self, client_id: UUID) -> None:
        async with self.clients_lock:
            self.clients.pop(client_id, None)

    async def get_client(self, client_id: UUID) -> Optional[ClientInfo]:
        async with self.clients_lock:
            return self.clients.get(client_id)

    async def update_client_poll_time(self, client_id: UUID) -> None:
        async with self.clients_lock:
            if client_id in self.clients:
                self.clients[client_id].last_poll = datetime.utcnow()

    async def add_floor_request(self, request: FloorRequest) -> None:
        async with self.requests_lock:
            self.floor_requests.add(request)
        await self.broadcast_update()

    async def remove_floor_request(self, request_id: UUID) -> bool:
        """Remove a pending call request (used by legacy /api/complete)."""
        found = False
        async with self.requests_lock:
            req = next((r for r in self.floor_requests if r.id == request_id), None)
            if req:
                self.floor_requests.discard(req)
                found = True
        if found:
            await self.broadcast_update()
        return found

    async def board_passenger(
        self, request_id: UUID, destination_floor: int
    ) -> Optional[PassengerRecord]:
        """Convert a call request into a boarded passenger.

        Removes the floor request and creates a PassengerRecord with the
        destination declared on the in-car panel.
        Returns the new PassengerRecord, or None if the request wasn't found.
        """
        call_floor = None
        async with self.requests_lock:
            req = next((r for r in self.floor_requests if r.id == request_id), None)
            if req:
                call_floor = req.floor
                self.floor_requests.discard(req)

        if call_floor is None:
            return None

        passenger = PassengerRecord(
            id=uuid4(),
            call_floor=call_floor,
            destination_floor=destination_floor,
            boarded_at=datetime.utcnow(),
        )
        async with self.passengers_lock:
            self.passengers[passenger.id] = passenger

        await self.broadcast_update()
        return passenger

    async def alight_passenger(self, passenger_id: UUID) -> bool:
        """Remove a passenger who has reached their destination floor."""
        found = False
        async with self.passengers_lock:
            if passenger_id in self.passengers:
                del self.passengers[passenger_id]
                found = True
        if found:
            await self.broadcast_update()
        return found

    async def get_passengers(self) -> list[PassengerRecord]:
        async with self.passengers_lock:
            return list(self.passengers.values())

    async def get_floor_requests(self) -> list[FloorRequest]:
        async with self.requests_lock:
            return sorted(self.floor_requests)

    async def get_elevator_state(self) -> ElevatorState:
        async with self.elevator_lock:
            return self.elevator_state.model_copy()

    async def update_elevator_floor(self, floor: int) -> None:
        async with self.elevator_lock:
            self.elevator_state.current_floor = floor
        await self.broadcast_update()

    async def update_elevator_direction(self, direction: Direction) -> None:
        async with self.elevator_lock:
            self.elevator_state.direction = direction
        await self.broadcast_update()

    async def set_operator(self, operator_id: Optional[UUID]) -> None:
        async with self.elevator_lock:
            self.elevator_state.operator_id = operator_id
        await self.broadcast_update()

    async def calculate_next_floor(self) -> tuple[Optional[int], Direction]:
        """Route using RL (with full passenger state) or fall back to SCAN."""
        async with self.elevator_lock, self.requests_lock:
            current_floor = self.elevator_state.current_floor
            direction = self.elevator_state.direction
            requests = set(self.floor_requests)

        async with self.passengers_lock:
            passengers = list(self.passengers.values())

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
                        passengers,
                    ),
                    timeout=3.0,
                )
                if rl_floor is not None:
                    return rl_floor, rl_dir
            except asyncio.TimeoutError:
                logger.warning("RL prediction timed out — falling back to SCAN")

        return calculate_next_floor(current_floor, direction, requests)

    async def get_state_update(self, use_rl: bool = False) -> FloorRequestUpdate:
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
        queue = asyncio.Queue(maxsize=100)
        async with self.subscribers_lock:
            self.subscribers.append(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        async with self.subscribers_lock:
            if queue in self.subscribers:
                self.subscribers.remove(queue)

    async def broadcast_update(self) -> None:
        update = await self.get_state_update()
        async with self.subscribers_lock:
            dead = []
            for queue in self.subscribers:
                try:
                    queue.put_nowait(update)
                except asyncio.QueueFull:
                    pass
                except Exception:
                    dead.append(queue)
            for queue in dead:
                self.subscribers.remove(queue)


state = ElevatorSystemState()
