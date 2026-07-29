"""FastAPI application with GraphQL support.

Main entry point for the elevator system backend.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from pathlib import Path
import logging
from uuid import UUID, uuid4
from datetime import datetime

from .schema import schema
from .config import settings
from .state import state
from .models import (
    RegisterRequest,
    CallElevatorRequest,
    CompleteFloorRequest,
    UpdateOperatorFloorRequest,
    BoardRequest,
    AlightRequest,
    ClientInfo,
    FloorRequest,
    Priority,
    ClientRole,
)
from .notifications import send_login_notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Elevator System API",
    description="Python/FastAPI/GraphQL migration of the Rust elevator system",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


# REST API endpoints for backwards compatibility with HTML frontend
@app.post("/api/register")
async def register_rest(request: RegisterRequest):
    """Register a new client (REST endpoint for backwards compatibility)."""
    try:
        client_id = uuid4()
        client = ClientInfo(
            id=client_id,
            role=request.role,
            last_poll=datetime.utcnow(),
        )
        await state.add_client(client)

        return {
            "type": "Welcome",
            "client_id": str(client_id),
        }
    except Exception as e:
        logger.error(f"Error in register: {e}")
        return JSONResponse(
            status_code=500,
            content={"type": "Error", "message": str(e)},
        )


@app.post("/api/call")
async def call_elevator_rest(request: CallElevatorRequest):
    """Call elevator to a floor (REST endpoint for backwards compatibility)."""
    try:
        request_id = uuid4()
        floor_request = FloorRequest(
            id=request_id,
            floor=request.floor,
            requested_at=datetime.utcnow(),
            priority=request.priority or Priority.NORMAL,
        )

        await state.add_floor_request(floor_request)

        return {
            "type": "Success",
            "message": f"Elevator called to floor {request.floor}",
            "request_id": str(request_id),
        }
    except Exception as e:
        logger.error(f"Error in call elevator: {e}")
        return JSONResponse(
            status_code=500,
            content={"type": "Error", "message": str(e)},
        )


@app.post("/api/complete")
async def complete_floor_rest(request: CompleteFloorRequest):
    """Complete a floor request (REST endpoint for backwards compatibility)."""
    try:
        success = await state.remove_floor_request(request.request_id)

        if success:
            return {
                "type": "Success",
                "message": "Floor request completed",
            }
        else:
            return JSONResponse(
                status_code=404,
                content={"type": "Error", "message": "Floor request not found"},
            )
    except Exception as e:
        logger.error(f"Error in complete floor: {e}")
        return JSONResponse(
            status_code=500,
            content={"type": "Error", "message": str(e)},
        )


@app.post("/api/board")
async def board_passenger_rest(request: BoardRequest):
    """Passenger boards elevator at call floor and declares destination.

    Called when the elevator arrives at the call floor and the passenger
    selects their destination on the in-car panel. Converts the pending
    floor request into an in-elevator PassengerRecord.
    """
    try:
        passenger = await state.board_passenger(request.request_id, request.destination_floor)
        if passenger:
            return {
                "type": "Boarded",
                "passenger_id": str(passenger.id),
                "destination_floor": passenger.destination_floor,
            }
        return JSONResponse(
            status_code=404,
            content={"type": "Error", "message": "Floor request not found"},
        )
    except Exception as e:
        logger.error(f"Error in board: {e}")
        return JSONResponse(status_code=500, content={"type": "Error", "message": str(e)})


@app.post("/api/alight")
async def alight_passenger_rest(request: AlightRequest):
    """Passenger alights at their destination floor.

    Called when the elevator arrives at the passenger's declared destination.
    Removes the PassengerRecord from in-elevator state.
    """
    try:
        success = await state.alight_passenger(request.passenger_id)
        if success:
            return {"type": "Success", "message": "Passenger alighted"}
        return JSONResponse(
            status_code=404,
            content={"type": "Error", "message": "Passenger not found"},
        )
    except Exception as e:
        logger.error(f"Error in alight: {e}")
        return JSONResponse(status_code=500, content={"type": "Error", "message": str(e)})


@app.post("/api/update")
async def update_operator_floor_rest(request: UpdateOperatorFloorRequest):
    """Update operator's current floor (REST endpoint for backwards compatibility)."""
    try:
        await state.update_elevator_floor(request.floor)

        return {
            "type": "Success",
            "message": f"Operator floor updated to {request.floor}",
        }
    except Exception as e:
        logger.error(f"Error in update operator floor: {e}")
        return JSONResponse(
            status_code=500,
            content={"type": "Error", "message": str(e)},
        )


@app.get("/api/poll")
async def poll_rest(client_id: str):
    """Poll for elevator updates (REST endpoint for backwards compatibility).

    This endpoint is kept for backwards compatibility with the HTML frontend.
    New clients should use GraphQL subscriptions instead.
    """
    try:
        # Validate client_id
        try:
            client_uuid = UUID(client_id)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"type": "Error", "message": "Invalid client ID"},
            )

        # Update client's last poll time
        await state.update_client_poll_time(client_uuid)

        # Get current state — use RL routing for poll responses
        update = await state.get_state_update(use_rl=True)

        return {
            "type": "FloorRequestUpdate",
            "requests": [
                {
                    "id": str(req.id),
                    "floor": req.floor,
                    "requested_at": req.requested_at.isoformat(),
                    "priority": req.priority.value,
                }
                for req in update.requests
            ],
            "next_floor": update.next_floor,
            "current_floor": update.current_floor,
            "direction": update.direction.value,
        }
    except Exception as e:
        logger.error(f"Error in poll: {e}")
        return JSONResponse(
            status_code=500,
            content={"type": "Error", "message": str(e)},
        )


@app.post("/api/login-notify")
async def login_notify_rest(request: Request):
    """Send login notification email (REST endpoint for backwards compatibility)."""
    try:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Send notification
        success = await send_login_notification(client_ip)

        if success:
            return {
                "type": "Success",
                "message": "Login notification sent",
            }
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "type": "Error",
                    "message": "Failed to send notification",
                },
            )
    except Exception as e:
        logger.error(f"Error in login notify: {e}")
        return JSONResponse(
            status_code=500,
            content={"type": "Error", "message": str(e)},
        )


# Static files - serve the HTML frontend
# Mount this last so it doesn't override API routes
static_path = Path(__file__).parent.parent.parent / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
    logger.info(f"Serving static files from {static_path}")
else:
    logger.warning(f"Static directory not found: {static_path}")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 60)
    logger.info("Elevator System Backend Starting")
    logger.info("=" * 60)
    logger.info(f"Port: {settings.port}")
    logger.info(f"GraphQL endpoint: http://localhost:{settings.port}/graphql")
    logger.info(f"GraphQL playground: http://localhost:{settings.port}/graphql")
    logger.info(f"Health check: http://localhost:{settings.port}/health")
    logger.info(f"REST API: http://localhost:{settings.port}/api/*")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Elevator System Backend Shutting Down")


def main():
    """Main entry point for the application."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
