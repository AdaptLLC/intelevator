# Elevator System - Python Backend

Python/FastAPI/GraphQL migration of the Rust elevator system with modern real-time subscriptions.

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

## License

Same as original Rust implementation.

## Support

For issues or questions, contact the development team.
