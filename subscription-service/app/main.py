from fastapi import FastAPI

from api import (
    publication,
    content,
    sales
)
from config.db.gino_db import db

app = FastAPI()


@app.on_event("startup")
async def initialize():
    engine = await db.set_bind(
        "postgresql+asyncpg://postgres:123@host.docker.internal:5432/public"
    )


@app.on_event("shutdown")
async def destroy():
    engine, db.bind = db.bind, None
    await engine.close()


app.include_router(publication.router, prefix="/ch08")
app.include_router(content.router, prefix="/ch08")
app.include_router(sales.router, prefix="/ch08")

