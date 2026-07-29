"""Data models for the elevator system."""
from enum import Enum
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from functools import total_ordering
from typing import Optional


class Priority(str, Enum):
    """Priority levels for floor requests."""
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"

    @property
    def value_int(self) -> int:
        """Return integer value for sorting (Emergency=2, High=1, Normal=0)."""
        return {"normal": 0, "high": 1, "emergency": 2}[self.value]


class Direction(str, Enum):
    """Direction enum for SCAN algorithm."""
    UP = "up"
    DOWN = "down"
    IDLE = "idle"


class ClientRole(str, Enum):
    """Client role types."""
    USER = "user"
    OPERATOR = "operator"
    SUPER = "super"


@total_ordering
class FloorRequest(BaseModel):
    """Floor request with priority ordering.

    Ordering: Higher priority first, then earlier timestamp, then floor number.
    """
    id: UUID
    floor: int
    requested_at: datetime
    priority: Priority = Priority.NORMAL

    def __eq__(self, other):
        """Equality based on ID."""
        if not isinstance(other, FloorRequest):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other):
        """Less-than for priority ordering (higher priority = "less than" for sorting).

        This matches Rust's ordering: emergency requests come first,
        then high priority, then normal. Within same priority, earlier
        timestamps come first, then lower floor numbers.
        """
        if not isinstance(other, FloorRequest):
            return NotImplemented

        # Compare priorities (reversed: higher priority = lower sort order)
        if self.priority.value_int != other.priority.value_int:
            return self.priority.value_int > other.priority.value_int

        # Same priority: compare timestamps (earlier = lower sort order)
        if self.requested_at != other.requested_at:
            return self.requested_at < other.requested_at

        # Same timestamp: compare floor numbers
        return self.floor < other.floor

    def __hash__(self):
        """Hash based on ID for use in sets."""
        return hash(self.id)


class ClientInfo(BaseModel):
    """Client information for session management."""
    id: UUID
    role: ClientRole
    last_poll: datetime


class ElevatorState(BaseModel):
    """Elevator state for routing algorithm."""
    current_floor: int = 1
    direction: Direction = Direction.IDLE
    operator_id: Optional[UUID] = None


class RegisterResponse(BaseModel):
    """Response for client registration."""
    client_id: UUID


class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str


class FloorRequestUpdate(BaseModel):
    """Update message with current elevator state."""
    requests: list[FloorRequest]
    next_floor: Optional[int]
    current_floor: int
    direction: Direction


class CallElevatorRequest(BaseModel):
    """Request to call elevator to a floor."""
    floor: int
    priority: Optional[Priority] = Priority.NORMAL


class CompleteFloorRequest(BaseModel):
    """Request to complete a floor."""
    request_id: UUID


class UpdateOperatorFloorRequest(BaseModel):
    """Request to update operator's current floor."""
    floor: int


class PassengerRecord(BaseModel):
    """A boarded passenger with a known destination.

    Created when the elevator arrives at a call floor and the passenger
    selects their destination on the in-car panel (/api/board).
    Removed when the elevator arrives at the destination (/api/alight).
    """
    id: UUID
    call_floor: int
    destination_floor: int
    boarded_at: datetime


class BoardRequest(BaseModel):
    """Passenger boards the elevator and declares destination."""
    request_id: UUID
    destination_floor: int


class AlightRequest(BaseModel):
    """Passenger alights at their destination floor."""
    passenger_id: UUID


class RegisterRequest(BaseModel):
    """Request to register a new client."""
    role: ClientRole
