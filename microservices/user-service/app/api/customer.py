from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import JSONResponse
from models.request.customer import CustomerReq
from models.data.nsms import Customer, Login
from repository.customer import CustomerRepository
from config.db.gino_db import db

import asyncio
import websockets
import json
from datetime import date, datetime
import logging.config

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

router = APIRouter()


def json_date_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def date_hook_deserializer(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            pass
    return json_dict


@router.post("/customer/add")
async def add_customer(req: CustomerReq):
    customer_dict = req.dict(exclude_unset=True)
    repo = CustomerRepository()

    logger.debug(f"Adding customer with data: {customer_dict}")

    result = await repo.insert_customer(customer_dict)
    if result:
        logger.info("Customer added successfully.")
        return req
    else:
        logger.error("Problem encountered while adding customer.")
        return JSONResponse(content={'message': 'Update customer profile problem encountered'}, status_code=500)


@router.websocket("/customer/list/ws")
async def customer_list_ws(websocket: WebSocket):
    await websocket.accept()
    repo = CustomerRepository()

    logger.debug("Fetching all customers for WebSocket connection.")

    result = await repo.get_all_customer()

    for rec in result:
        data = rec.to_dict()
        await websocket.send_json(json.dumps(data, default=json_date_serializer))
        await asyncio.sleep(0.01)

        client_resp = await websocket.receive_json()
        logger.info(f"Acknowledging receipt of record id {client_resp['rec_id']}.")

    await websocket.close()
    logger.info("WebSocket connection closed.")


@router.get("/customer/wsclient/list/")
async def customer_list_ws_client():
    uri = "ws://localhost:8000/ch08/customer/list/ws"

    logger.debug("Connecting to WebSocket for customer list.")

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                res = await websocket.recv()
                data_json = json.loads(res, object_hook=date_hook_deserializer)

                logger.info(f"Received record: {data_json}.")

                data_dict = json.loads(data_json)
                client_resp = {"rec_id": data_dict['id']}
                await websocket.send(json.dumps(client_resp))

            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed.")
                break

    logger.info("WebSocket client operation completed.")
    return {"message": "done"}