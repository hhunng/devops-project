from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.request.subscription import SubscriptionReq
from models.data.nsms import Customer, Subscription
from repository.subscription import SubscriptionRepository, SubscriptionCustomerRepository
from config.db.gino_db import db

import rx.operators as ops
from rx.scheduler.eventloop import AsyncIOScheduler
from services.subscription import fetch_records, fetch_subscription

import asyncio
from datetime import date
import logging

import logging.config

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/subscription/add")
async def add_subscription(req: SubscriptionReq):
    subscription_dict = req.dict(wlude_unset=True)
    repo = SubscriptionRepository()
    logger.debug(f"Adding subscription with data: {subscription_dict}")

    result = await repo.insert_subscription(subscription_dict)
    if result:
        logger.info("Subscription added successfully.")
        return req
    else:
        logger.error("Problem encountered while updating subscription.")
        return JSONResponse(content={'message': 'Update subscription problem encountered'}, status_code=500)


@router.get("/subscription/list/all")
async def list_all_subscriptions():
    repo = SubscriptionRepository()
    logger.debug("Fetching all subscriptions.")

    result = await repo.get_all_subscription()
    result_map = [u.to_dict() for u in result]

    logger.info(f"Fetched {len(result_map)} subscriptions.")
    return result_map


@router.post("/subscription/dated")
async def list_dated_subscription(min_date: date, max_date: date):
    logger.debug(f"Fetching subscriptions from {min_date} to {max_date}.")

    loop = asyncio.get_event_loop()
    observable = await fetch_subscription(min_date, max_date, loop)

    observable.subscribe(
        on_next=lambda item: logger.info(f"Subscription details: {item}."),
        scheduler=AsyncIOScheduler(loop)
    )

    return {"message": "Subscription details are being processed."}


@router.get("/subscription/monitor/total")
async def list_all_customer_subscription():
    logger.debug("Creating background task to fetch total customer subscriptions.")

    loop = asyncio.get_event_loop()
    observable = fetch_records(5, loop)

    observable.subscribe(
        on_next=lambda item: logger.info(f"The total amount sold: {item}."),
        scheduler=AsyncIOScheduler(loop)
    )

    logger.info("Background task for total customer subscriptions created.")
    return {"content": "Background task created."}