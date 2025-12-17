from contextlib import asynccontextmanager
import logging
import pathlib
import sys

from domain.stats import StatsResponse
from fastapi import FastAPI, Request
from middleware.request_tracker import RequestTracker
from storage.factory import get_storage


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - web_counter - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Initialize storage
storage = get_storage(storage_type="disk")

# Initialize request tracker
tracker = RequestTracker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    yield
    logger.info("Web Counter API shutting down")

    # Cleanup: delete counter file if exists
    counter_file = "counter.txt"
    if pathlib.Path(counter_file).exists():
        pathlib.Path(counter_file).unlink()
        logger.info(f"Deleted {counter_file}")


# Initialize FastAPI app
app = FastAPI(title="Web Counter API", lifespan=lifespan)


@app.middleware("http")
async def track_inc_requests(request: Request, call_next):
    """Middleware to track all incoming requests."""
    response = await call_next(request)
    if request.url.path == "/inc":  # Track only /inc requests
        await tracker.record()
    return response


@app.post("/inc")
async def increment_counter():
    """Increment the counter by 1 and return the new value."""
    new_value = await storage.increment()
    logger.info(f"Counter incremented to {new_value}")
    return {"count": new_value}


@app.get("/count")
async def get_counter():
    """Get the current counter value."""
    current_value = await storage.get_count()
    logger.info(f"Counter value retrieved: {current_value}")
    return {"count": current_value}


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get RPS statistics."""
    return await tracker.get_stats()
