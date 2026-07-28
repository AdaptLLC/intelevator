# Elevator System - Python Backend

Python/FastAPI/GraphQL migration of the Rust elevator system with modern real-time subscriptions and PPO reinforcement learning routing.

## Running the API and Simulation

**Terminal 1 — start the API:**
```bash
cd Elevator_API
uv run uvicorn app.main:app --port 8000
```

**Terminal 2 — run the real-time RL simulation:**
```bash
cd Elevator_API
uv run python simulate.py
```

The simulation registers as an operator, spawns random floor requests every 1–4 seconds, and displays a live building visualisation showing the elevator moving, floors with pending requests, and a running tally of requests served vs. spawned. The PPO model (`models/ppo_checkpoint_ep1688.zip`) routes all decisions; if the model times out (>3s), routing falls back to SCAN automatically.

To update the RL checkpoint to a newer training episode:
1. Copy the desired zip from `../Elevator_Reinforcement_Training/checkpoints_episode/` into `models/`.
2. Update `_MODEL_PATH` in `app/state.py` to point to the new filename.
3. Restart the API.

## Overview

This backend replaces the original Rust implementation (Warp + Tokio) with a modern Python stack:

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Strawberry GraphQL**: Type-safe GraphQL with Python type hints
- **GraphQL Subscriptions**: Real-time updates via WebSocket (replaces HTTP polling)
- **Pydantic**: Data validation and settings management
- **Resend**: Email notifications

## Features

- **SCAN Elevator Algorithm**: Efficient routing with priority handling
- **Priority Queue**: Emergency > High > Normal priority levels
- **Real-time Updates**: GraphQL subscriptions for instant state changes
- **Backwards Compatible**: REST endpoints for existing HTML frontend
- **Email Notifications**: Login alerts via Resend API
- **Type Safety**: Full type hints and Pydantic validation

## Client Roles

Three roles are supported:

- **USER** — building occupant calling the elevator to a floor
- **OPERATOR** — the person physically operating the elevator, reports current floor position
- **SUPER** — superintendent or building manager with elevated access

## Quick Start

### Option A: Using UV (Recommended - Faster)

[UV](https://github.com/astral-sh/uv) is a blazing-fast Python package installer and resolver written in Rust.

```bash
cd backend

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode with uv
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Option B: Using Standard Pip

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in editable mode
pip install -e .

# Or install from requirements.txt (legacy)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Required Environment Variables

Edit `.env` with your settings:
- `RESEND_API_KEY`: Get from https://resend.com/api-keys
- `ADMIN_EMAIL`: Email address for login notifications

### Alternative: Run with Script Entry Point

After installing in editable mode, you can also run:

```bash
elevator-system
```

The server will start on http://localhost:8000

## Endpoints

### GraphQL

- **GraphQL Playground**: http://localhost:8000/graphql
- **GraphQL API**: http://localhost:8000/graphql

Use the interactive playground to explore queries, mutations, and subscriptions.

### REST API (Backwards Compatibility)

The following REST endpoints are available for compatibility with the existing HTML frontend:

- `POST /api/register` - Register a new client
- `POST /api/call` - Call elevator to a floor
- `POST /api/complete` - Complete a floor request
- `POST /api/update` - Update operator's floor
- `GET /api/poll?client_id=<uuid>` - Poll for updates (legacy)
- `POST /api/login-notify` - Send login notification

### Health Check

- `GET /health` - Health check endpoint

## GraphQL API

### Queries

```graphql
# Get current elevator status
query {
  elevatorStatus {
    currentFloor
    nextFloor
    direction
    requests {
      id
      floor
      priority
      requestedAt
    }
  }
}

# Get all pending requests
query {
  floorRequests {
    id
    floor
    priority
    requestedAt
  }
}
```

### Mutations

```graphql
# Register a new client
mutation {
  register(role: USER) {
    clientId
  }
}

# Call elevator to a floor
mutation {
  callElevator(floor: 5, priority: NORMAL) {
    id
    floor
    priority
    requestedAt
  }
}

# Complete a floor request
mutation {
  completeFloor(requestId: "uuid-here") {
    message
    success
  }
}

# Update operator's floor
mutation {
  updateOperatorFloor(floor: 3) {
    message
    success
  }
}

# Send login notification
mutation {
  loginNotify(clientIp: "192.168.1.1") {
    message
    success
  }
}
```

### Subscriptions

```graphql
# Subscribe to real-time elevator updates
subscription {
  elevatorUpdates {
    currentFloor
    nextFloor
    direction
    requests {
      id
      floor
      priority
      requestedAt
    }
  }
}
```

The subscription will push updates whenever:
- A new floor is called
- A floor request is completed
- The operator updates their position

## Architecture

### Core Components

1. **models.py** - Pydantic data models with priority ordering
2. **algorithm.py** - SCAN elevator routing algorithm
3. **state.py** - Shared state management with asyncio locks
4. **schema.py** - GraphQL schema (queries, mutations, subscriptions)
5. **main.py** - FastAPI application with GraphQL router
6. **config.py** - Configuration management (environment variables)
7. **notifications.py** - Email notifications via Resend

### State Management

The system uses `asyncio.Lock` for thread-safe state management:

- **Clients**: Dictionary of active client sessions
- **Floor Requests**: Set of pending requests (priority-sorted)
- **Elevator State**: Current floor, direction, operator ID
- **Subscribers**: List of WebSocket connections for real-time updates

### SCAN Algorithm

The SCAN (elevator) algorithm efficiently routes the elevator:

1. **Emergency Priority**: Jump to emergency requests immediately
2. **Directional Scanning**: Continue in current direction until exhausted
3. **Direction Reversal**: Switch directions when no more floors in current direction
4. **Idle Behavior**: When idle, select the closest floor

### Real-time Updates

GraphQL subscriptions replace HTTP polling:

**Old (Rust)**: HTTP polling every 1 second
```javascript
setInterval(() => fetch('/api/poll?client_id=...'), 1000);
```

**New (Python)**: GraphQL subscription over WebSocket
```graphql
subscription {
  elevatorUpdates { ... }
}
```

Benefits:
- Instant updates (no 1-second delay)
- Reduced server load (no constant polling)
- Automatic reconnection handling
- Bi-directional communication

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── schema.py            # GraphQL schema
│   ├── models.py            # Pydantic data models
│   ├── state.py             # State management
│   ├── algorithm.py         # SCAN algorithm
│   └── notifications.py     # Email notifications
├── pyproject.toml          # Modern Python package config
├── requirements.txt         # Python dependencies (legacy)
├── .env.example            # Environment template
├── .env                    # Your environment (not in git)
└── README.md               # This file
```

### Running Tests

```bash
# Install dev dependencies (with uv)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"

# Run tests (when implemented)
pytest
```

### Code Quality

The project includes mypy and ruff in dev dependencies:

```bash
# Type checking
mypy app/

# Linting
ruff check app/

# Formatting
ruff format app/

# Fix linting issues automatically
ruff check --fix app/
```

## Migration Notes

### Changes from Rust Version

**Kept:**
- SCAN algorithm logic (proven, well-documented)
- Priority queue ordering (Emergency > High > Normal)
- Email notifications via Resend
- Access control pattern
- REST API compatibility

**Replaced:**
- HTTP polling → GraphQL subscriptions (cleaner real-time)
- Dapr pub/sub → Python asyncio (simpler for single-server)
- Warp → FastAPI (more Pythonic, better docs)
- Arc<RwLock> → asyncio.Lock (Python equivalent)

**Improved:**
- Secrets moved to environment variables (no more hardcoded API keys)
- Better logging with Python logging module
- Type safety with Pydantic and type hints
- Interactive GraphQL playground for testing

### Backwards Compatibility

The REST endpoints ensure the existing HTML frontend continues to work without modifications. New clients should use the GraphQL API for better performance and real-time features.

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t elevator-system .
docker run -p 8000:8000 --env-file .env elevator-system
```

### Production Considerations

1. **Environment Variables**: Never commit `.env` file
2. **HTTPS**: Use reverse proxy (nginx, Caddy) for TLS
3. **CORS**: Set specific origins in production
4. **Rate Limiting**: Add slowapi middleware
5. **Monitoring**: Use logging and health checks
6. **Database**: Consider Redis for multi-instance deployments

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Email Notifications Not Working

1. Check `RESEND_API_KEY` is set correctly
2. Verify API key at https://resend.com/api-keys
3. Check email address is valid
4. Review logs for error messages

### WebSocket Connection Issues

1. Ensure WebSocket support in reverse proxy (nginx)
2. Check firewall allows WebSocket connections
3. Verify CORS settings allow your origin

## RL Integration Roadmap

The current API routes elevator calls using the SCAN algorithm. The roadmap below describes how the trained PPO model from `Elevator_Reinforcement_Training` will be integrated into the API and continuously improved through a feedback loop with live operations.

The API configuration targets 3 elevators and 10 floors, matching the training environment exactly. This is a hard requirement — the PPO model's observation vector is fixed at the shape produced by that configuration and cannot accept a different elevator count without retraining.

### Model training

No trained checkpoint is committed to the repo. Training must be run before Phase 1 can proceed. The `Elevator_Reinforcement_Training/training.py` script runs 500 episodes across 12 parallel environments and saves a versioned checkpoint after each episode. On CPU this takes several hours. The recommended path is a GPU instance (AWS g4dn.xlarge or Google Colab) to reduce training time to under an hour. The output file `ppo_maskable_elevator_model.zip` is committed to `models/` and loaded by the API at startup.

### Phase 1 — Connect the trained model to the API ✓ Complete

`rl_router.py` is wired into `state.py`. The PPO model is a step-based controller: each call to `model.predict(obs, action_masks=masks)` returns one action per elevator (wait, up, or down) for a single simulation timestep. The API is event-driven — it receives a floor call and must return a target floor. A mini-simulation loop in `rl_router.py` runs the model forward from the current building state until it commits an elevator to a floor target. Predictions run in a `ThreadPoolExecutor` so they don't block the FastAPI event loop, with a 3-second timeout that falls back to SCAN if the model doesn't converge. The poll endpoint uses RL routing; broadcast updates use SCAN to keep the event loop clear.

### Phase 2 — Operational event logging

Every boarding and dropoff event carries the data needed to compute the reward signal: wait time, ride time, floor, and timestamp. These events are written to a Supabase Postgres instance via the standard asyncpg driver using the connection string from environment variables. A background job replays recent operational episodes through the simulation environment to generate training data shaped by real building traffic rather than synthetic spawning alone. Supabase is used for the POC; migration to a self-hosted or cloud-managed Postgres instance (via Terraform or Bicep) is straightforward when the project moves to production deployment.

### Phase 3 — Continuous retraining

A scheduled job (nightly or weekly) takes the accumulated operational logs, runs a `resume_training.py` pass using the current model checkpoint as the starting point, and saves a new versioned checkpoint. The API loads the updated model at startup or via a hot-reload endpoint without requiring a full restart.

### Phase 4 — Decision logging and drift data collection

On every routing decision, the API logs both what SCAN would have chosen and what the RL model chose, along with the full observation vector at the time of the decision and the resulting outcome (wait time, ride time) when the request completes. This side-by-side record is the foundation for drift detection. Automated fallback to SCAN is not triggered in this phase. The threshold for automated fallback will be calibrated from this logged data after enough real decisions accumulate to establish a meaningful baseline. The logging schema and a read query for comparing SCAN vs. RL outcomes over rolling time windows are defined in `app/event_log.py`.

### Planned additions to project structure

```
Elevator_API/
├── app/
│   ├── algorithm.py         # SCAN algorithm (baseline, used for comparison logging)
│   ├── rl_router.py         # PPO model loader, mini-simulation loop, predict wrapper ✓
│   ├── event_log.py         # Operational event logging and decision comparison to Supabase (Phase 2)
│   └── ...
├── models/
│   └── ppo_checkpoint_ep1688.zip  # Trained checkpoint — episode 1688 ✓
├── jobs/
│   └── retrain.py           # Scheduled retraining job (Phase 3)
├── simulate.py              # Real-time terminal simulation with Rich dashboard ✓
```

## License

Same as original Rust implementation.

## Support

For issues or questions, contact the development team.
