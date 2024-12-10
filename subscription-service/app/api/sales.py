from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models.request.sales import SalesReq
from models.data.nsms import Sales, Publication
from repository.sales import SalesRepository
from config.db.gino_db import db
from services.sales import create_observable

import rx
import asyncio
from rx.scheduler import ThreadPoolScheduler
from rx.scheduler.eventloop import AsyncIOScheduler
import multiprocessing
import logging.config

# Set up thread pool scheduler
thread_count = multiprocessing.cpu_count()
thread_pool_scheduler = ThreadPoolScheduler(thread_count)

router = APIRouter()


@router.post("/sales/add")
async def add_sales(req: SalesReq):
    sales_dict = req.dict(exclude_unset=True)
    repo = SalesRepository()

    logger.debug(f"Adding sales with data: {sales_dict}")

    result = await repo.insert_sales(sales_dict)
    if result:
        logger.info("Sales added successfully.")
        return req
    else:
        logger.error("Problem encountered while adding sales.")
        return JSONResponse(content={'message': 'Update sales problem encountered'}, status_code=500)


@router.get("/sales/list/quota")
async def list_sales_by_quota():
    loop = asyncio.get_event_loop()
    observer = create_observable(loop)

    logger.debug("Subscribing to sales quota notifications.")

    observer.subscribe(
        on_next=lambda value: logger.info(f"Received instruction to buy: {value}"),
        on_completed=lambda: logger.info("Completed trades"),
        on_error=lambda e: logger.error(f"Error occurred: {e}"),
        scheduler=AsyncIOScheduler(loop)
    )

    logger.info("Notification process started in the background.")
    return {"message": "Notification sent in the background"}