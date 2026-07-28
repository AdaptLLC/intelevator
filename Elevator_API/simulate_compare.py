"""Side-by-side PPO vs SCAN simulation.

Both elevators receive identical floor requests. The PPO elevator routes
through the live API (GET /api/poll). The SCAN elevator is driven entirely
in-process using algorithm.calculate_next_floor — no second API instance needed.

Usage:
    # Terminal 1 — start the API
    uv run uvicorn app.main:app --port 8000

    # Terminal 2 — run the comparison
    uv run python simulate_compare.py
"""
import asyncio
import random
import httpx
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

# Add app to path so we can import algorithm directly
sys.path.insert(0, os.path.dirname(__file__))
from app.algorithm import calculate_next_floor
from app.models import Direction, FloorRequest, Priority
from uuid import uuid4

BASE = "http://localhost:8000"
NUM_FLOORS = 10
SPAWN_INTERVAL = 2.0
POLL_INTERVAL = 1.0
SIM_DURATION = 120

console = Console()


@dataclass
class ElevatorState:
    name: str
    floor: int = 1
    direction: str = "idle"
    next_floor: Optional[int] = None
    served: int = 0
    total_wait_steps: int = 0
    served_per_floor: dict = field(default_factory=lambda: defaultdict(int))


@dataclass
class Request:
    id: str           # simulation-local ID
    api_id: str       # UUID returned by /api/call — used for /api/complete
    floor: int
    spawned_step: int


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def build_panel(state: ElevatorState, requests: list[Request], step: int, color: str) -> Panel:
    pending_floors: dict[int, int] = defaultdict(int)
    for r in requests:
        pending_floors[r.floor] += 1

    lines = []
    for f in range(NUM_FLOORS, 0, -1):
        if f == state.floor:
            arrow = {"up": "▲", "down": "▼", "idle": "■"}.get(state.direction, "■")
            elev = f"[bold {color}][{arrow}][/bold {color}]"
        else:
            elev = "   "

        target = f" [cyan]←[/cyan]" if f == state.next_floor and f != state.floor else ""
        waiting = f"  [yellow]{pending_floors[f]}w[/yellow]" if f in pending_floors else ""
        served = f" [green]✓{state.served_per_floor[f]}[/green]" if state.served_per_floor[f] else ""
        lines.append(f"  {f:2d} {elev}{target}{waiting}{served}")

    dir_color = {"up": "green", "down": "red", "idle": "yellow"}.get(state.direction, "white")
    next_str = str(state.next_floor) if state.next_floor else "—"
    avg_wait = f"{state.total_wait_steps / state.served:.1f}" if state.served else "—"

    status = (
        f"Floor [bold]{state.floor}[/bold]  "
        f"[bold {dir_color}]{state.direction.upper()}[/bold {dir_color}]  "
        f"→[cyan]{next_str}[/cyan]\n"
        f"Served [bold green]{state.served}[/bold green]  "
        f"Pending [bold]{len(requests)}[/bold]  "
        f"Avg wait [bold]{avg_wait}[/bold] steps"
    )

    content = "\n".join(lines) + "\n\n" + status
    return Panel(content, title=f"[bold {color}]{state.name}[/bold {color}]", border_style=color)


def build_display(
    ppo: ElevatorState,
    scan: ElevatorState,
    ppo_reqs: list[Request],
    scan_reqs: list[Request],
    log_lines: list[str],
    elapsed: float,
    total_spawned: int,
) -> Table:
    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(
        build_panel(ppo, ppo_reqs, int(elapsed), "blue"),
        build_panel(scan, scan_reqs, int(elapsed), "magenta"),
    )

    log_display = "\n".join(log_lines[-6:]) if log_lines else "—"
    footer = Panel(
        f"[dim]{elapsed:.0f}s / {SIM_DURATION}s   Spawned: {total_spawned}[/dim]\n{log_display}",
        title="[dim]Event log[/dim]",
        border_style="dim",
    )

    outer = Table.grid(expand=True)
    outer.add_column()
    outer.add_row(grid)
    outer.add_row(footer)
    return outer


async def run():
    log_lines: list[str] = []
    total_spawned = 0

    ppo = ElevatorState(name="PPO (RL Model)")
    scan = ElevatorState(name="SCAN (Baseline)")

    # Pending requests for each elevator — both receive same floor set
    ppo_reqs: list[Request] = []
    scan_reqs: list[Request] = []

    # SCAN internal direction state (pure in-process, no API)
    scan_direction = Direction.IDLE

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Register PPO elevator as operator
        resp = await client.post(f"{BASE}/api/register", json={"role": "operator"})
        client_id = resp.json()["client_id"]
        await client.post(f"{BASE}/api/update", json={"floor": 1})
        log_lines.append(f"{ts()}  Registered PPO operator {client_id[:8]}…")

        loop = asyncio.get_event_loop()
        start = loop.time()
        next_spawn = start + random.uniform(1.0, SPAWN_INTERVAL)
        step = 0

        with Live(
            build_display(ppo, scan, ppo_reqs, scan_reqs, log_lines, 0, total_spawned),
            refresh_per_second=4,
            console=console,
        ) as live:

            while loop.time() - start < SIM_DURATION:
                now = loop.time()
                elapsed = now - start

                # ── Spawn a request (both elevators get it) ──────────────────
                if now >= next_spawn:
                    floor = random.randint(1, NUM_FLOORS)
                    total_spawned += 1
                    log_lines.append(f"{ts()}  Request → floor {floor}")
                    scan_reqs.append(Request(id=str(uuid4()), api_id="", floor=floor, spawned_step=step))

                    # Register with API — capture the API-assigned UUID for completions
                    api_id = str(uuid4())  # fallback if call fails
                    try:
                        api_resp = await client.post(f"{BASE}/api/call", json={"floor": floor})
                        if api_resp.status_code == 200:
                            api_id = api_resp.json().get("request_id", api_id)
                    except Exception:
                        pass
                    ppo_reqs.append(Request(id=str(uuid4()), api_id=api_id, floor=floor, spawned_step=step))

                    next_spawn = now + random.uniform(1.5, SPAWN_INTERVAL * 2)

                # ── PPO elevator: poll API for RL routing decision ────────────
                # The API runs the PPO model and returns next_floor. If the model
                # stalls (returns current floor with requests pending), we fall back
                # to SCAN in-process — matching what state.py does on timeout.
                ppo_direction_model = Direction.IDLE
                try:
                    poll = await client.get(f"{BASE}/api/poll", params={"client_id": client_id})
                    if poll.status_code == 200:
                        data = poll.json()
                        ppo.next_floor = data["next_floor"]
                except Exception as e:
                    log_lines.append(f"{ts()}  [PPO poll skipped: {type(e).__name__}]")

                # If RL gave no useful target, fall back to SCAN in-process
                if (not ppo.next_floor or ppo.next_floor == ppo.floor) and ppo_reqs:
                    ppo_req_set = {
                        FloorRequest(
                            id=uuid4(), floor=r.floor,
                            requested_at=datetime.now(timezone.utc), priority=Priority.NORMAL,
                        )
                        for r in ppo_reqs
                    }
                    ppo_direction_enum = {"up": Direction.UP, "down": Direction.DOWN}.get(
                        ppo.direction, Direction.IDLE
                    )
                    ppo.next_floor, ppo_direction_model = calculate_next_floor(
                        ppo.floor, ppo_direction_enum, ppo_req_set
                    )

                # Move one step
                if ppo.next_floor and ppo.next_floor != ppo.floor:
                    target = ppo.floor + (1 if ppo.next_floor > ppo.floor else -1)
                    ppo.direction = "up" if target > ppo.floor else "down"
                    try:
                        await client.post(f"{BASE}/api/update", json={"floor": target})
                        ppo.floor = target
                    except Exception:
                        ppo.direction = "idle"
                else:
                    ppo.direction = "idle"

                # Complete PPO requests at current floor
                served_ppo = [r for r in ppo_reqs if r.floor == ppo.floor]
                for r in served_ppo:
                    try:
                        cr = await client.post(
                            f"{BASE}/api/complete", json={"request_id": r.api_id}
                        )
                        if cr.status_code == 200:
                            wait = step - r.spawned_step
                            ppo.total_wait_steps += wait
                            ppo.served += 1
                            ppo.served_per_floor[ppo.floor] += 1
                            ppo_reqs.remove(r)
                    except Exception:
                        pass

                # ── SCAN elevator: pure in-process routing ───────────────────
                scan_request_set = {
                    FloorRequest(
                        id=uuid4(), floor=r.floor,
                        requested_at=datetime.now(timezone.utc), priority=Priority.NORMAL
                    )
                    for r in scan_reqs
                }
                scan_next, scan_direction = calculate_next_floor(
                    scan.floor, scan_direction, scan_request_set
                )
                scan.next_floor = scan_next

                if scan_next and scan_next != scan.floor:
                    target = scan.floor + (1 if scan_next > scan.floor else -1)
                    scan.direction = "up" if target > scan.floor else "down"
                    scan.floor = target
                else:
                    scan.direction = "idle"

                # Complete SCAN requests at current floor
                served_scan = [r for r in scan_reqs if r.floor == scan.floor]
                for r in served_scan:
                    wait = step - r.spawned_step
                    scan.total_wait_steps += wait
                    scan.served += 1
                    scan.served_per_floor[scan.floor] += 1
                    scan_reqs.remove(r)

                step += 1
                live.update(
                    build_display(ppo, scan, ppo_reqs, scan_reqs, log_lines, elapsed, total_spawned)
                )
                await asyncio.sleep(POLL_INTERVAL)

    # Final summary
    ppo_avg = f"{ppo.total_wait_steps / ppo.served:.1f}" if ppo.served else "n/a"
    scan_avg = f"{scan.total_wait_steps / scan.served:.1f}" if scan.served else "n/a"
    console.print(f"\n[bold]── Final Results ──[/bold]")
    console.print(f"  [blue]PPO [/blue]  served [bold]{ppo.served}[/bold]/{total_spawned}  avg wait {ppo_avg} steps")
    console.print(f"  [magenta]SCAN[/magenta]  served [bold]{scan.served}[/bold]/{total_spawned}  avg wait {scan_avg} steps")
    winner = "PPO" if ppo.served >= scan.served else "SCAN"
    console.print(f"\n  [bold green]{winner} served more requests.[/bold green]\n")


if __name__ == "__main__":
    asyncio.run(run())
