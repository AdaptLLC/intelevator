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
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

BASE = "http://localhost:8000"
NUM_FLOORS = 10
SPAWN_INTERVAL = 2.0   # seconds between random floor requests
POLL_INTERVAL = 1.0    # seconds between display refreshes
SIM_DURATION = 120     # seconds to run

console = Console()
log_lines: list[str] = []


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def build_display(current_floor: int, direction: str, next_floor, requests: list) -> Panel:
    request_floors = {r["floor"] for r in requests}

    # Building visualisation — top floor to bottom
    building_lines = []
    for f in range(NUM_FLOORS, 0, -1):
        elevator = ""
        if f == current_floor:
            arrow = {"up": "▲", "down": "▼", "idle": "■"}.get(direction, "■")
            elevator = f" [{arrow}]"
        waiting = f"  ← {sum(1 for r in requests if r['floor'] == f)} waiting" if f in request_floors else ""
        floor_label = f"  Floor {f:2d}{elevator}{waiting}"
        building_lines.append(floor_label)

    building = "\n".join(building_lines)

    next_str = str(next_floor) if next_floor else "—"
    dir_color = {"up": "green", "down": "red", "idle": "yellow"}.get(direction, "white")

    status = (
        f"Current floor: [bold]{current_floor}[/bold]  "
        f"Direction: [bold {dir_color}]{direction.upper()}[/bold {dir_color}]  "
        f"Next target: [bold cyan]{next_str}[/bold cyan]  "
        f"Pending requests: [bold]{len(requests)}[/bold]"
    )

    log_display = "\n".join(log_lines[-8:]) if log_lines else "—"

    content = f"{building}\n\n{status}\n\n[dim]── Event log ──[/dim]\n{log_display}"
    return Panel(content, title="[bold]Intelevator RL Simulation[/bold]", border_style="blue")


async def run():
    async with httpx.AsyncClient(timeout=30.0) as client:

        # Register as operator
        resp = await client.post(f"{BASE}/api/register", json={"role": "operator"})
        client_id = resp.json()["client_id"]
        log_lines.append(f"{ts()}  Registered as operator {client_id[:8]}…")

        # Set starting floor
        await client.post(f"{BASE}/api/update", json={"floor": 1})

        start = asyncio.get_event_loop().time()
        next_spawn = start + random.uniform(1.0, SPAWN_INTERVAL)

        with Live(build_display(1, "idle", None, []), refresh_per_second=4, console=console) as live:
            current_floor = 1
            direction = "idle"
            next_floor = None
            requests = []

            while asyncio.get_event_loop().time() - start < SIM_DURATION:
                now = asyncio.get_event_loop().time()

                # Spawn a random floor request
                if now >= next_spawn:
                    floor = random.randint(1, NUM_FLOORS)
                    resp = await client.post(f"{BASE}/api/call", json={"floor": floor})
                    if resp.status_code == 200:
                        log_lines.append(f"{ts()}  Request → floor {floor}")
                    next_spawn = now + random.uniform(1.5, SPAWN_INTERVAL * 2)

                # Poll state
                poll = await client.get(f"{BASE}/api/poll", params={"client_id": client_id})
                if poll.status_code == 200:
                    data = poll.json()
                    current_floor = data["current_floor"]
                    direction = data["direction"]
                    next_floor = data["next_floor"]
                    requests = data["requests"]

                    # Move elevator one step toward next_floor
                    if next_floor and next_floor != current_floor:
                        new_floor = current_floor + (1 if next_floor > current_floor else -1)
                        await client.post(f"{BASE}/api/update", json={"floor": new_floor})
                        log_lines.append(
                            f"{ts()}  Elevator {current_floor}→{new_floor}  "
                            f"(target {next_floor}, {direction})"
                        )
                        current_floor = new_floor

                        # Complete requests at this floor
                        served = [r for r in requests if r["floor"] == new_floor]
                        for r in served:
                            await client.post(f"{BASE}/api/complete", json={"request_id": r["id"]})
                            log_lines.append(f"{ts()}  Served floor {new_floor} ✓")

                live.update(build_display(current_floor, direction, next_floor, requests))
                await asyncio.sleep(POLL_INTERVAL)

        console.print(f"\n[green]Simulation complete — {len(log_lines)} events logged.[/green]")


if __name__ == "__main__":
    asyncio.run(run())
