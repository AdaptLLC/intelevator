"""Side-by-side PPO vs SCAN simulation.

Both elevators receive identical floor requests. The PPO elevator routes
through the live API using the full board/alight lifecycle so the RL model
gets a complete observation (waiting per floor + passengers aboard +
destination histogram). The SCAN elevator runs entirely in-process.

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
class SimElevator:
    name: str
    floor: int = 1
    direction: str = "idle"
    next_floor: Optional[int] = None
    served: int = 0
    total_wait_steps: int = 0
    served_per_floor: dict = field(default_factory=lambda: defaultdict(int))


@dataclass
class PendingCall:
    """A floor call not yet picked up."""
    id: str           # local sim ID
    api_id: str       # UUID returned by /api/call — used for /api/board
    floor: int
    spawned_step: int


@dataclass
class BoardedPassenger:
    """A passenger aboard the elevator heading to destination_floor."""
    passenger_id: str   # UUID returned by /api/board
    call_floor: int
    destination_floor: int
    boarded_step: int


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def build_panel(
    elev: SimElevator,
    calls: list[PendingCall],
    aboard: list[BoardedPassenger],
    color: str,
) -> Panel:
    pending_floors: dict[int, int] = defaultdict(int)
    for c in calls:
        pending_floors[c.floor] += 1
    dest_floors: dict[int, int] = defaultdict(int)
    for p in aboard:
        dest_floors[p.destination_floor] += 1

    lines = []
    for f in range(NUM_FLOORS, 0, -1):
        if f == elev.floor:
            arrow = {"up": "▲", "down": "▼", "idle": "■"}.get(elev.direction, "■")
            elev_str = f"[bold {color}][{arrow}][/bold {color}]"
        else:
            elev_str = "   "

        target = " [cyan]←[/cyan]" if f == elev.next_floor and f != elev.floor else ""
        waiting = f"  [yellow]{pending_floors[f]}w[/yellow]" if f in pending_floors else ""
        dests = f"  [magenta]{dest_floors[f]}↓[/magenta]" if f in dest_floors else ""
        done = f" [green]✓{elev.served_per_floor[f]}[/green]" if elev.served_per_floor[f] else ""
        lines.append(f"  {f:2d} {elev_str}{target}{waiting}{dests}{done}")

    dir_color = {"up": "green", "down": "red", "idle": "yellow"}.get(elev.direction, "white")
    next_str = str(elev.next_floor) if elev.next_floor else "—"
    avg_wait = f"{elev.total_wait_steps / elev.served:.1f}" if elev.served else "—"

    status = (
        f"Floor [bold]{elev.floor}[/bold]  "
        f"[bold {dir_color}]{elev.direction.upper()}[/bold {dir_color}]  "
        f"→[cyan]{next_str}[/cyan]\n"
        f"Served [bold green]{elev.served}[/bold green]  "
        f"Calls [bold]{len(calls)}[/bold]  "
        f"Aboard [bold]{len(aboard)}[/bold]  "
        f"Avg wait [bold]{avg_wait}[/bold]"
    )

    content = "\n".join(lines) + "\n\n" + status
    return Panel(content, title=f"[bold {color}]{elev.name}[/bold {color}]", border_style=color)


def build_display(
    ppo: SimElevator, ppo_calls: list, ppo_aboard: list,
    scan: SimElevator, scan_calls: list,
    log_lines: list[str], elapsed: float, total_spawned: int,
) -> Table:
    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(
        build_panel(ppo, ppo_calls, ppo_aboard, "blue"),
        build_panel(scan, scan_calls, [], "magenta"),
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

    ppo = SimElevator(name="PPO (RL Model)")
    scan = SimElevator(name="SCAN (Baseline)")

    ppo_calls: list[PendingCall] = []
    ppo_aboard: list[BoardedPassenger] = []
    scan_calls: list[PendingCall] = []
    scan_direction = Direction.IDLE

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{BASE}/api/register", json={"role": "operator"})
        client_id = resp.json()["client_id"]
        await client.post(f"{BASE}/api/update", json={"floor": 1})
        log_lines.append(f"{ts()}  Registered PPO operator {client_id[:8]}…")

        loop = asyncio.get_event_loop()
        start = loop.time()
        next_spawn = start + random.uniform(1.0, SPAWN_INTERVAL)
        step = 0

        with Live(
            build_display(ppo, ppo_calls, ppo_aboard, scan, scan_calls, log_lines, 0, total_spawned),
            refresh_per_second=4,
            console=console,
        ) as live:

            while loop.time() - start < SIM_DURATION:
                now = loop.time()
                elapsed = now - start

                # ── Spawn identical call to both elevators ────────────────────
                if now >= next_spawn:
                    floor = random.randint(1, NUM_FLOORS)
                    total_spawned += 1
                    log_lines.append(f"{ts()}  Call → floor {floor}")
                    scan_calls.append(PendingCall(id=str(uuid4()), api_id="", floor=floor, spawned_step=step))

                    api_id = str(uuid4())
                    try:
                        r = await client.post(f"{BASE}/api/call", json={"floor": floor})
                        if r.status_code == 200:
                            api_id = r.json().get("request_id", api_id)
                    except Exception:
                        pass
                    ppo_calls.append(PendingCall(id=str(uuid4()), api_id=api_id, floor=floor, spawned_step=step))
                    next_spawn = now + random.uniform(1.5, SPAWN_INTERVAL * 2)

                # ── PPO elevator: get routing from API ────────────────────────
                try:
                    poll = await client.get(f"{BASE}/api/poll", params={"client_id": client_id})
                    if poll.status_code == 200:
                        ppo.next_floor = poll.json()["next_floor"]
                except Exception as e:
                    log_lines.append(f"{ts()}  [poll err: {type(e).__name__}]")

                # Fallback to in-process SCAN if RL gives no useful target
                all_ppo_targets = ppo_calls + [
                    PendingCall(id="", api_id="", floor=p.destination_floor, spawned_step=0)
                    for p in ppo_aboard
                ]
                if (not ppo.next_floor or ppo.next_floor == ppo.floor) and all_ppo_targets:
                    req_set = {
                        FloorRequest(
                            id=uuid4(), floor=t.floor,
                            requested_at=datetime.now(timezone.utc), priority=Priority.NORMAL,
                        )
                        for t in all_ppo_targets
                    }
                    dir_enum = {"up": Direction.UP, "down": Direction.DOWN}.get(ppo.direction, Direction.IDLE)
                    ppo.next_floor, _ = calculate_next_floor(ppo.floor, dir_enum, req_set)

                # Move PPO one step
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

                # Board PPO passengers at current floor (call → board with random dest)
                for c in [c for c in ppo_calls if c.floor == ppo.floor]:
                    dest = random.randint(1, NUM_FLOORS)
                    while dest == ppo.floor:
                        dest = random.randint(1, NUM_FLOORS)
                    try:
                        br = await client.post(
                            f"{BASE}/api/board",
                            json={"request_id": c.api_id, "destination_floor": dest},
                        )
                        if br.status_code == 200:
                            pid = br.json()["passenger_id"]
                            wait = step - c.spawned_step
                            ppo_aboard.append(BoardedPassenger(
                                passenger_id=pid, call_floor=c.floor,
                                destination_floor=dest, boarded_step=step,
                            ))
                            ppo_calls.remove(c)
                            log_lines.append(f"{ts()}  PPO boarded f{ppo.floor}→{dest}")
                    except Exception:
                        pass

                # Alight PPO passengers at destination
                for p in [p for p in ppo_aboard if p.destination_floor == ppo.floor]:
                    try:
                        ar = await client.post(
                            f"{BASE}/api/alight", json={"passenger_id": p.passenger_id}
                        )
                        if ar.status_code == 200:
                            wait = step - p.boarded_step
                            ppo.total_wait_steps += wait
                            ppo.served += 1
                            ppo.served_per_floor[ppo.floor] += 1
                            ppo_aboard.remove(p)
                            log_lines.append(f"{ts()}  PPO alighted f{ppo.floor} ✓")
                    except Exception:
                        pass

                # ── SCAN elevator: pure in-process ────────────────────────────
                scan_req_set = {
                    FloorRequest(
                        id=uuid4(), floor=c.floor,
                        requested_at=datetime.now(timezone.utc), priority=Priority.NORMAL,
                    )
                    for c in scan_calls
                }
                scan_next, scan_direction = calculate_next_floor(scan.floor, scan_direction, scan_req_set)
                scan.next_floor = scan_next

                if scan_next and scan_next != scan.floor:
                    target = scan.floor + (1 if scan_next > scan.floor else -1)
                    scan.direction = "up" if target > scan.floor else "down"
                    scan.floor = target
                else:
                    scan.direction = "idle"

                for c in [c for c in scan_calls if c.floor == scan.floor]:
                    wait = step - c.spawned_step
                    scan.total_wait_steps += wait
                    scan.served += 1
                    scan.served_per_floor[scan.floor] += 1
                    scan_calls.remove(c)

                step += 1
                live.update(build_display(
                    ppo, ppo_calls, ppo_aboard, scan, scan_calls, log_lines, elapsed, total_spawned
                ))
                await asyncio.sleep(POLL_INTERVAL)

    ppo_avg = f"{ppo.total_wait_steps / ppo.served:.1f}" if ppo.served else "n/a"
    scan_avg = f"{scan.total_wait_steps / scan.served:.1f}" if scan.served else "n/a"
    console.print("\n[bold]── Final Results ──[/bold]")
    console.print(f"  [blue]PPO [/blue]  served [bold]{ppo.served}[/bold]/{total_spawned}  avg wait {ppo_avg} steps")
    console.print(f"  [magenta]SCAN[/magenta]  served [bold]{scan.served}[/bold]/{total_spawned}  avg wait {scan_avg} steps")
    winner = "PPO" if ppo.served >= scan.served else "SCAN"
    console.print(f"\n  [bold green]{winner} served more requests.[/bold green]\n")


if __name__ == "__main__":
    asyncio.run(run())
