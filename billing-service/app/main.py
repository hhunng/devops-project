from fastapi import FastAPI
import os
from api import billing, subscription
from config.db.gino_db import db
import logging

# Initialize logger
logger = logging.getLogger(__name__)

app = FastAPI(docs_url="/billing", redoc_url=None)
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")

@app.on_event("startup")
async def initialize():
    try:
        await db.set_bind(f"postgresql+asyncpg://postgres:{POSTGRES_PASSWORD}@postgresql:5432/public")
        logger.info("Database connected successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def destroy():
    # Ensure that db.bind is set before trying to close it
    if db.bind:
        engine = db.bind
        db.bind = None
        await engine.close()

# Include routers with a prefix
app.include_router(billing.router, prefix="/ch08")
app.include_router(subscription.router, prefix="/ch08")