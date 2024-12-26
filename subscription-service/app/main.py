from fastapi import FastAPI
import os
import logging
from api import publication, content, sales
from config.db.gino_db import db

# Initialize logger
logger = logging.getLogger(__name__)

app = FastAPI(docs_url="/subscription", redoc_url=None)
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
app.include_router(publication.router, prefix="/ch08")
app.include_router(content.router, prefix="/ch08")
app.include_router(sales.router, prefix="/ch08")