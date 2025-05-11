# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, swap_router, transfer_router, webhook_router
from app.routers.historical_transaction_router import router as historical_transaction_router
from app.routers.user_balance_router import router as user_balance_router
from app.routers.scheduler_router import router as scheduler_router
from app.scheduler.user_balance_scheduler import balance_scheduler
from app.scheduler.transaction_scheduler import transaction_scheduler
from app.utils.database_util import run_migrations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):

    # run_migrations()
    
    # Startup: Configure and start the background schedulers
    
    # Schedule an hourly snapshot at minute 0 of each hour
    balance_scheduler.schedule_hourly_snapshots(minute=0)
    
    # Schedule a transaction fetch at minute 0 of each hour
    transaction_scheduler.schedule_transaction_fetch(minute=45)
    
    # Start the schedulers
    balance_scheduler.start()
    transaction_scheduler.start()
    logging.info("Background schedulers started")
    
    yield
    
    # Shutdown: Clean up resources
    balance_scheduler.shutdown()
    transaction_scheduler.shutdown()
    logging.info("Background schedulers shutdown")

app = FastAPI(
    title="Excution Agent API",
    description="API for executing transactions and tracking user token balances and calculating portfolio value",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(swap_router.router)
app.include_router(transfer_router.router)
app.include_router(webhook_router.router)
app.include_router(historical_transaction_router)
app.include_router(user_balance_router)
app.include_router(scheduler_router)

@app.get("/")
async def root():
    return {
        "message": "User Balance Tracking API is running",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logging.info(f"Request: {request.method} {request.url.path}")
#     response = await call_next(request)
#     return response

# @app.middleware("http")
# async def log_webhook_body(request: Request, call_next):
#     # Only log webhook request bodies
#     if "/webhook/" in request.url.path:
#         body = await request.body()
#         logging.info(f"Webhook request body: {body.decode()}")
#         # Need to reset the request body since we've consumed it
#         request._body = body
    
#     response = await call_next(request)
#     return response
