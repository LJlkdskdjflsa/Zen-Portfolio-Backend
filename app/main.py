# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.utils.database_util import run_migrations
from app.routers import optimization

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # run_migrations()
    logging.info("Background schedulers started")

    yield

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
app.include_router(optimization.router)


@app.get("/")
async def root():
    return {
        "message": "User Balance Tracking API is running",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }
