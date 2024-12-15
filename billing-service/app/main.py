from fastapi import FastAPI

from api import (
    billing,
    subscription
)
from config.db.gino_db import db

app = FastAPI(docs_url="/billing", redoc_url=None)
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", "default_password")

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
    engine, db.bind = db.bind, None
    await engine.close()

app.include_router(billing.router, prefix="/ch08")
app.include_router(subscription.router, prefix="/ch08")
