"""SCAN elevator algorithm adapted for MultiElevatorEnv.

Operates on the training environment's native state — Guest objects,
Elevator objects — so it can be called from the eval callback without
any translation layer.
"""


def scan_action(elevator, waiting_guests, num_floors=10):
    """Return the SCAN action (0=wait, 1=up, 2=down) for a single elevator.

    Mirrors the logic in Elevator_API/app/algorithm.py but operates on the
    training env's data structures rather than FloorRequest objects.
    """
    # Collect all target floors: waiting guests + passengers aboard
    waiting_floors = [g.current_floor for g in waiting_guests]
    dest_floors = [p.target_floor for p in elevator.passengers]
    all_targets = set(waiting_floors + dest_floors)

    if not all_targets:
        return 0  # wait — nothing to do

    current = elevator.current_floor

    # If guests can board or alight here, wait (open doors)
    leaving = [p for p in elevator.passengers if p.target_floor == current]
    boarding = [g for g in waiting_guests if g.current_floor == current]
    if leaving or (boarding and len(elevator.passengers) < elevator.capacity):
        return 0  # wait

    # SCAN: determine direction from passenger destinations first,
    # then from waiting guests.
    floors_above = [f for f in all_targets if f > current]
    floors_below = [f for f in all_targets if f < current]

    # Prefer to continue in the direction that has the closest target.
    if floors_above and floors_below:
        nearest_above = min(floors_above) - current
        nearest_below = current - max(floors_below)
        if nearest_above <= nearest_below:
            return 1  # up
        return 2  # down
    elif floors_above:
        return 1  # up
    elif floors_below:
        return 2  # down

    return 0  # wait


def run_scan_episode(env_fn, num_floors=10, max_steps=10000):
    """Run a complete episode using SCAN and return the total reward.

    env_fn: callable that returns a fresh (unwrapped) MultiElevatorEnv instance.
    max_steps: hard cap to keep eval callback fast (matches PPO eval cap).
    """
    import numpy as np
    env = env_fn()
    obs, info = env.reset()
    # Unwrap ActionMasker (or any wrapper) to access native env attributes
    inner = getattr(env, "env", env)
    total_reward = 0.0
    done = False
    steps = 0

    while not done and steps < max_steps:
        actions = []
        for elev in inner.elevators:
            actions.append(scan_action(elev, inner.waiting_guests, num_floors))
        obs, reward, done, truncated, info = env.step(np.array(actions))
        total_reward += reward
        steps += 1
        if truncated:
            break

    env.close()
    return total_reward
