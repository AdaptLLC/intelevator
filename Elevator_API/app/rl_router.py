"""PPO-based elevator routing using a trained Maskable PPO checkpoint.

Translates the step-level PPO action output (wait/up/down) into a target floor
decision compatible with the existing calculate_next_floor() signature.
"""
import logging
from pathlib import Path
from typing import Optional, Set

import numpy as np

from .models import Direction, FloorRequest, Priority

logger = logging.getLogger(__name__)

# Actions from the training environment
ACTION_WAIT = 0
ACTION_UP = 1
ACTION_DOWN = 2

# Observation constants matching MultiElevatorEnv
NUM_ELEVATORS = 3
NUM_FLOORS = 10
OBS_PER_ELEVATOR = 2 + NUM_FLOORS  # floor + passengers + destination histogram

_model = None
_model_path: Optional[Path] = None
_num_model_elevators: int = 1  # derived from loaded model's action space


def load_model(model_path: Path) -> bool:
    """Load the PPO checkpoint. Returns True on success."""
    global _model, _model_path, _num_model_elevators
    try:
        from sb3_contrib import MaskablePPO

        _model = MaskablePPO.load(str(model_path))
        _model_path = model_path
        # Derive elevator count from action space: MultiDiscrete([3]*N) -> N
        _num_model_elevators = len(_model.action_space.nvec)
        logger.info(
            "RL router loaded checkpoint: %s (elevators: %d)",
            model_path.name,
            _num_model_elevators,
        )
        return True
    except Exception as exc:
        logger.warning("RL router unavailable — falling back to SCAN: %s", exc)
        _model = None
        return False


def _build_obs(current_floor: int, requests: Set[FloorRequest]) -> np.ndarray:
    """Build a 46-element observation vector from live API state.

    The observation space is always 3-elevator × 12 features + 10 waiting floors = 46,
    matching the training environment. Elevator 0 carries live state; the rest are zeroed.
    API floors are 1-indexed; the training env is 0-indexed.
    """
    obs = []

    # Elevator 0: live state (shift to 0-indexed)
    obs.append(max(0, current_floor - 1))
    obs.append(0)  # passengers unknown at API level
    obs.extend([0] * NUM_FLOORS)  # destination histogram unknown

    # Elevators 1 and 2: zeroed regardless of model action space size
    for _ in range(NUM_ELEVATORS - 1):
        obs.append(0)
        obs.append(0)
        obs.extend([0] * NUM_FLOORS)

    # Waiting guests per floor derived from floor requests
    waiting_per_floor = [0] * NUM_FLOORS
    for req in requests:
        floor_idx = req.floor - 1
        if 0 <= floor_idx < NUM_FLOORS:
            waiting_per_floor[floor_idx] += 1
    obs.extend(waiting_per_floor)

    return np.array(obs, dtype=np.int32)


def _all_actions_mask() -> np.ndarray:
    """Return a flat action mask allowing all moves.

    MaskablePPO with MultiDiscrete([3]*N) expects a flat array of length N*3.
    Uses the actual elevator count from the loaded model's action space.
    """
    return np.ones(_num_model_elevators * 3, dtype=bool)


def _direction_from_action(action: int) -> Direction:
    if action == ACTION_UP:
        return Direction.UP
    if action == ACTION_DOWN:
        return Direction.DOWN
    return Direction.IDLE


def calculate_next_floor_rl(
    current_floor: int,
    direction: Direction,
    requests: Set[FloorRequest],
    max_steps: int = 20,
) -> tuple[Optional[int], Direction]:
    """Return (target_floor, direction) using the PPO model.

    Runs a mini-simulation loop stepping the model from the current floor
    until it lands on a floor with a pending request. Falls back to None
    (caller should use SCAN) if the model is unavailable or no target is
    reached within max_steps.
    """
    if _model is None:
        return None, direction

    if not requests:
        return None, Direction.IDLE

    # Emergency requests bypass RL — immediate priority
    emergency = next(
        (r for r in requests if r.priority == Priority.EMERGENCY), None
    )
    if emergency:
        target = emergency.floor
        if target > current_floor:
            return target, Direction.UP
        if target < current_floor:
            return target, Direction.DOWN
        return target, Direction.IDLE

    request_floors = {r.floor for r in requests}
    sim_floor = current_floor  # 1-indexed (API convention)

    for _ in range(max_steps):
        obs = _build_obs(sim_floor, requests)

        # In the mini-sim we force a directional decision: mask out wait unless
        # the elevator is already at a requested floor (where waiting is meaningful).
        at_request = sim_floor in request_floors
        can_go_up = sim_floor < NUM_FLOORS
        can_go_down = sim_floor > 1
        mask = np.array([
            at_request,   # wait only valid when at a pending request floor
            can_go_up,
            can_go_down,
        ], dtype=bool)
        # Replicate mask across all elevator slots the model expects
        action_masks = np.tile(mask, _num_model_elevators)

        try:
            actions, _ = _model.predict(
                obs, action_masks=action_masks, deterministic=True
            )
        except Exception as exc:
            logger.warning("RL predict error: %s", exc)
            return None, direction

        if hasattr(actions, "__len__"):
            elevator_action = int(actions.flat[0])
        else:
            elevator_action = int(actions)

        if elevator_action == ACTION_UP and can_go_up:
            sim_floor += 1
        elif elevator_action == ACTION_DOWN and can_go_down:
            sim_floor -= 1

        if sim_floor in request_floors:
            new_dir = _direction_from_action(elevator_action)
            if new_dir == Direction.IDLE:
                if sim_floor > current_floor:
                    new_dir = Direction.UP
                elif sim_floor < current_floor:
                    new_dir = Direction.DOWN
            return sim_floor, new_dir

    # Model didn't converge — fall back to SCAN
    logger.debug("RL router did not converge in %d steps; falling back", max_steps)
    return None, direction
