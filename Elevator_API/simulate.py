"""Real-time simulation of the Elevator API with RL routing.

Spawns floor requests at random intervals and polls the API to show
the RL model's routing decisions live in the terminal.

Usage:
    # In one terminal: start the API
    uv run uvicorn app.main:app --port 8000

    # In another terminal:
    uv run python simulate.py
"""
import asyncio
import random
import httpx
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

BASE = "http://localhost:8000"
NUM_FLOORS = 10
SPAWN_INTERVAL = 2.0   # seconds between random floor requests
POLL_INTERVAL = 1.0    # seconds between display refreshes
SIM_DURATION = 120     # seconds to run

console = Console()
log_lines: list[str] = []
served_counts: dict[int, int] = defaultdict(int)
total_requested = 0
total_served = 0


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def build_display(current_floor: int, direction: str, next_floor, requests: list, elapsed: float) -> Panel:
    request_floors: dict[int, int] = defaultdict(int)
    for r in requests:
        request_floors[r["floor"]] += 1

    building_lines = []
    for f in range(NUM_FLOORS, 0, -1):
        # Elevator indicator
        if f == current_floor:
            arrow = {"up": "▲", "down": "▼", "idle": "■"}.get(direction, "■")
            elev = f" [{arrow}]"
        else:
            elev = "    "

        # Target marker
        target_mark = " [cyan]←target[/cyan]" if f == next_floor and f != current_floor else ""

        # Waiting count
        waiting = f"  [yellow]{request_floors[f]} waiting[/yellow]" if f in request_floors else ""

        # Served count (persists across sim)
        served = f"  [green]✓{served_counts[f]}[/green]" if served_counts[f] else ""

        building_lines.append(f"  Floor {f:2d}{elev}{target_mark}{waiting}{served}")

    building = "\n".join(building_lines)

    dir_color = {"up": "green", "down": "red", "idle": "yellow"}.get(direction, "white")
    next_str = str(next_floor) if next_floor else "—"

    status = (
        f"Floor: [bold]{current_floor}[/bold]  "
        f"Dir: [bold {dir_color}]{direction.upper()}[/bold {dir_color}]  "
        f"Target: [bold cyan]{next_str}[/bold cyan]  "
        f"Pending: [bold]{len(requests)}[/bold]  "
        f"Served: [bold green]{total_served}[/bold green]/[bold]{total_requested}[/bold]  "
        f"[dim]{elapsed:.0f}s / {SIM_DURATION}s[/dim]"
    )

    log_display = "\n".join(log_lines[-8:]) if log_lines else "—"
    content = f"{building}\n\n{status}\n\n[dim]── Event log ──[/dim]\n{log_display}"
    return Panel(content, title="[bold]Intelevator RL Simulation[/bold]", border_style="blue")


async def run():
    global total_requested, total_served

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Register as operator
        resp = await client.post(f"{BASE}/api/register", json={"role": "operator"})
        client_id = resp.json()["client_id"]
        log_lines.append(f"{ts()}  Registered as operator {client_id[:8]}…")

        # Set starting floor
        await client.post(f"{BASE}/api/update", json={"floor": 1})

        loop = asyncio.get_event_loop()
        start = loop.time()
        next_spawn = start + random.uniform(1.0, SPAWN_INTERVAL)

        with Live(build_display(1, "idle", None, [], 0), refresh_per_second=4, console=console) as live:
            current_floor = 1
            direction = "idle"
            next_floor = None
            requests = []

            while loop.time() - start < SIM_DURATION:
                now = loop.time()
                elapsed = now - start

                # Spawn a random floor request
                if now >= next_spawn:
                    floor = random.randint(1, NUM_FLOORS)
                    try:
                        resp = await client.post(f"{BASE}/api/call", json={"floor": floor})
                        if resp.status_code == 200:
                            total_requested += 1
                            log_lines.append(f"{ts()}  Request → floor {floor}")
                    except Exception:
                        pass
                    next_spawn = now + random.uniform(1.5, SPAWN_INTERVAL * 2)

                # Poll state
                try:
                    poll = await client.get(f"{BASE}/api/poll", params={"client_id": client_id})
                    if poll.status_code == 200:
                        data = poll.json()
                        current_floor = data["current_floor"]
                        next_floor = data["next_floor"]
                        requests = data["requests"]

                        # Move one step toward next_floor; track direction locally
                        # (API always returns direction=idle — it never receives direction updates)
                        if next_floor and next_floor != current_floor:
                            target = current_floor + (1 if next_floor > current_floor else -1)
                            direction = "up" if target > current_floor else "down"
                            try:
                                await client.post(f"{BASE}/api/update", json={"floor": target})
                                log_lines.append(
                                    f"{ts()}  {current_floor}→{target} (target {next_floor}, {direction})"
                                )
                                current_floor = target
                            except Exception:
                                direction = "idle"
                        else:
                            direction = "idle"

                        # Complete any requests at the floor we are now on.
                        # Only runs after the move committed (current_floor already updated above).
                        served = [r for r in requests if r["floor"] == current_floor]
                        for r in served:
                            try:
                                resp = await client.post(
                                    f"{BASE}/api/complete", json={"request_id": r["id"]}
                                )
                                if resp.status_code == 200:
                                    served_counts[current_floor] += 1
                                    total_served += 1
                                    log_lines.append(f"{ts()}  Served floor {current_floor} ✓")
                            except Exception:
                                pass

                except Exception as e:
                    log_lines.append(f"{ts()}  [poll skipped: {type(e).__name__}]")

                live.update(build_display(current_floor, direction, next_floor, requests, elapsed))
                await asyncio.sleep(POLL_INTERVAL)

        console.print(
            f"\n[green]Simulation complete — "
            f"{total_served}/{total_requested} requests served, "
            f"{len(log_lines)} events logged.[/green]"
        )


if __name__ == "__main__":
    asyncio.run(run())
