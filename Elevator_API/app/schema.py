"""GraphQL schema using Strawberry.

Defines types, queries, mutations, and subscriptions.
"""
import strawberry
from enum import Enum
from typing import Optional, AsyncGenerator
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from .models import (
    Priority,
    Direction,
    ClientRole,
    FloorRequest as FloorRequestModel,
    ClientInfo as ClientInfoModel,
    FloorRequestUpdate as FloorRequestUpdateModel,
)
from .state import state


# GraphQL types
@strawberry.enum
class PriorityEnum(str, Enum):
    """Priority levels for floor requests."""
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"


@strawberry.enum
class DirectionEnum(str, Enum):
    """Direction of elevator movement."""
    UP = "up"
    DOWN = "down"
    IDLE = "idle"


@strawberry.enum
class ClientRoleEnum(str, Enum):
    """Client role types."""
    USER = "user"
    OPERATOR = "operator"
    SUPER = "super"


@strawberry.type
class FloorRequest:
    """A floor request with priority."""
    id: strawberry.ID
    floor: int
    requested_at: datetime
    priority: PriorityEnum

    @classmethod
    def from_model(cls, model: FloorRequestModel) -> "FloorRequest":
        """Convert from Pydantic model to GraphQL type."""
        return cls(
            id=strawberry.ID(str(model.id)),
            floor=model.floor,
            requested_at=model.requested_at,
            priority=PriorityEnum(model.priority.value),
        )


@strawberry.type
class ElevatorStatus:
    """Current elevator status."""
    current_floor: int
    next_floor: Optional[int]
    direction: DirectionEnum
    requests: list[FloorRequest]


@strawberry.type
class RegisterResponse:
    """Response when a client registers."""
    client_id: strawberry.ID


@strawberry.type
class SuccessResponse:
    """Generic success response."""
    message: str
    success: bool = True


# Queries
@strawberry.type
class Query:
    """GraphQL queries for reading elevator state."""

    @strawberry.field
    async def elevator_status(self) -> ElevatorStatus:
        """Get current elevator status with all pending requests."""
        update = await state.get_state_update()
        return ElevatorStatus(
            current_floor=update.current_floor,
            next_floor=update.next_floor,
            direction=DirectionEnum(update.direction.value),
            requests=[FloorRequest.from_model(req) for req in update.requests],
        )

    @strawberry.field
    async def floor_requests(self) -> list[FloorRequest]:
        """Get all pending floor requests."""
        requests = await state.get_floor_requests()
        return [FloorRequest.from_model(req) for req in requests]


# Mutations
@strawberry.type
class Mutation:
    """GraphQL mutations for modifying elevator state."""

    @strawberry.mutation
    async def register(self, role: ClientRoleEnum) -> RegisterResponse:
        """Register a new client session.

        Args:
            role: The role of the client (user, operator, super)

        Returns:
            RegisterResponse with client_id
        """
        client_id = uuid4()
        client = ClientInfoModel(
            id=client_id,
            role=ClientRole(role.value),
            last_poll=datetime.utcnow(),
        )
        await state.add_client(client)

        return RegisterResponse(client_id=strawberry.ID(str(client_id)))

    @strawberry.mutation
    async def call_elevator(
        self,
        floor: int,
        priority: Optional[PriorityEnum] = PriorityEnum.NORMAL,
    ) -> FloorRequest:
        """Call elevator to a specific floor.

        Args:
            floor: The floor number to call the elevator to
            priority: Priority level (normal, high, emergency)

        Returns:
            The created FloorRequest
        """
        request_id = uuid4()
        priority_value = Priority(priority.value) if priority else Priority.NORMAL

        request = FloorRequestModel(
            id=request_id,
            floor=floor,
            requested_at=datetime.utcnow(),
            priority=priority_value,
        )

        await state.add_floor_request(request)

        return FloorRequest.from_model(request)

    @strawberry.mutation
    async def complete_floor(self, request_id: strawberry.ID) -> SuccessResponse:
        """Mark a floor request as completed.

        Args:
            request_id: The ID of the floor request to complete

        Returns:
            Success response
        """
        try:
            request_uuid = UUID(str(request_id))
        except ValueError:
            return SuccessResponse(
                message="Invalid request ID format",
                success=False,
            )

        success = await state.remove_floor_request(request_uuid)

        if success:
            return SuccessResponse(message="Floor request completed successfully")
        else:
            return SuccessResponse(
                message="Floor request not found",
                success=False,
            )

    @strawberry.mutation
    async def update_operator_floor(self, floor: int) -> SuccessResponse:
        """Update the operator's current floor position.

        Args:
            floor: The floor number the operator is currently on

        Returns:
            Success response
        """
        await state.update_elevator_floor(floor)

        return SuccessResponse(message=f"Operator floor updated to {floor}")

    @strawberry.mutation
    async def login_notify(self, client_ip: Optional[str] = None) -> SuccessResponse:
        """Send login notification email.

        Args:
            client_ip: IP address of the client (optional)

        Returns:
            Success response
        """
        from .notifications import send_login_notification

        ip_address = client_ip or "unknown"
        success = await send_login_notification(ip_address)

        if success:
            return SuccessResponse(message="Login notification sent")
        else:
            return SuccessResponse(
                message="Failed to send notification",
                success=False,
            )


# Subscriptions
@strawberry.type
class Subscription:
    """GraphQL subscriptions for real-time updates."""

    @strawberry.subscription
    async def elevator_updates(
        self,
        info: strawberry.Info,
    ) -> AsyncGenerator[ElevatorStatus, None]:
        """Subscribe to real-time elevator status updates.

        This replaces HTTP polling with WebSocket-based GraphQL subscriptions.
        Clients will receive updates whenever the elevator state changes.

        Yields:
            ElevatorStatus messages when state changes occur
        """
        # Subscribe to state updates
        queue = await state.subscribe()

        try:
            # Send initial state
            initial_update = await state.get_state_update()
            yield ElevatorStatus(
                current_floor=initial_update.current_floor,
                next_floor=initial_update.next_floor,
                direction=DirectionEnum(initial_update.direction.value),
                requests=[FloorRequest.from_model(req) for req in initial_update.requests],
            )

            # Stream updates as they occur
            while True:
                try:
                    # Wait for next update with timeout
                    update: FloorRequestUpdateModel = await asyncio.wait_for(
                        queue.get(),
                        timeout=30.0,
                    )

                    yield ElevatorStatus(
                        current_floor=update.current_floor,
                        next_floor=update.next_floor,
                        direction=DirectionEnum(update.direction.value),
                        requests=[FloorRequest.from_model(req) for req in update.requests],
                    )

                except asyncio.TimeoutError:
                    # Send keepalive with current state
                    keepalive_update = await state.get_state_update()
                    yield ElevatorStatus(
                        current_floor=keepalive_update.current_floor,
                        next_floor=keepalive_update.next_floor,
                        direction=DirectionEnum(keepalive_update.direction.value),
                        requests=[FloorRequest.from_model(req) for req in keepalive_update.requests],
                    )

        except GeneratorExit:
            # Client disconnected, clean up
            await state.unsubscribe(queue)
            raise
        except Exception as e:
            # Error occurred, clean up
            await state.unsubscribe(queue)
            raise


# Create schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
