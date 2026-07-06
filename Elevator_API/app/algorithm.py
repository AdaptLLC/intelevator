"""SCAN elevator routing algorithm implementation.

Ported from src/main.rs:135-197
"""
from typing import Optional, Set
from .models import FloorRequest, Direction, Priority


def calculate_next_floor(
    current_floor: int,
    direction: Direction,
    requests: Set[FloorRequest],
) -> tuple[Optional[int], Direction]:
    """Calculate the next floor to visit using the SCAN algorithm.

    Priority rules:
    1. Emergency requests have absolute priority
    2. SCAN algorithm: continue in current direction until no more floors
    3. If idle, select the closest floor

    Args:
        current_floor: Current elevator floor position
        direction: Current direction of travel
        requests: Set of pending floor requests

    Returns:
        Tuple of (next_floor, new_direction)
        - next_floor: None if no requests, otherwise the floor number
        - new_direction: Direction for the elevator to move
    """
    if not requests:
        return (None, Direction.IDLE)

    # Extract all requested floors
    floors = [req.floor for req in requests]

    # Handle emergency requests first - they jump to the front
    emergency_req = next(
        (req for req in requests if req.priority == Priority.EMERGENCY),
        None
    )
    if emergency_req:
        emergency_floor = emergency_req.floor
        if emergency_floor > current_floor:
            return (emergency_floor, Direction.UP)
        elif emergency_floor < current_floor:
            return (emergency_floor, Direction.DOWN)
        else:
            return (emergency_floor, Direction.IDLE)

    # SCAN algorithm: continue in current direction until exhausted
    if direction == Direction.UP:
        # Find next floor above current position
        floors_above = [f for f in floors if f > current_floor]
        if floors_above:
            next_floor = min(floors_above)
            return (next_floor, Direction.UP)
        else:
            # No more floors above, switch to going down
            floors_below = [f for f in floors if f < current_floor]
            if floors_below:
                next_floor = max(floors_below)
                return (next_floor, Direction.DOWN)
            else:
                return (None, Direction.IDLE)

    elif direction == Direction.DOWN:
        # Find next floor below current position
        floors_below = [f for f in floors if f < current_floor]
        if floors_below:
            next_floor = max(floors_below)
            return (next_floor, Direction.DOWN)
        else:
            # No more floors below, switch to going up
            floors_above = [f for f in floors if f > current_floor]
            if floors_above:
                next_floor = min(floors_above)
                return (next_floor, Direction.UP)
            else:
                return (None, Direction.IDLE)

    elif direction == Direction.IDLE:
        # Find the closest floor
        if not floors:
            return (None, Direction.IDLE)

        closest_floor = min(floors, key=lambda f: abs(f - current_floor))

        # Determine direction to closest floor
        if closest_floor > current_floor:
            new_direction = Direction.UP
        elif closest_floor < current_floor:
            new_direction = Direction.DOWN
        else:
            new_direction = Direction.IDLE

        return (closest_floor, new_direction)

    return (None, Direction.IDLE)
