from fastapi import FastAPI
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api import login, admin, vendor, customer
from config.db.gino_db import db

app = FastAPI(docs_url="/user", redoc_url=None)
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
    if db.bind is not None:
        await db.pop_bind().close()
        logger.info("Database connection closed.")


app.include_router(login.router, prefix="/ch08")
app.include_router(admin.router, prefix="/ch08")
app.include_router(vendor.router, prefix="/ch08")
app.include_router(customer.router, prefix="/ch08")
