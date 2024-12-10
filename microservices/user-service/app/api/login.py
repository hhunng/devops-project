from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.request.login import LoginReq
from models.data.nsms import Login
from repository.login import LoginRepository
from config.db.gino_db import db

from services.login import build_user_list, count_login
import asyncio
import logging.config

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/login/add")
async def add_login(req: LoginReq):
    login_dict = req.dict(exclude_unset=True)
    repo = LoginRepository()

    logger.debug(f"Adding login with data: {login_dict}")

    result = await repo.insert_login(login_dict)
    if result:
        logger.info("Login added successfully.")
        return req
    else:
        logger.error("Problem encountered while inserting login profile.")
        return JSONResponse(content={'message': 'Insert login profile problem encountered'}, status_code=500)


@router.patch("/login/update")
async def update_login(id: int, req: LoginReq):
    login_dict = req.dict(exclude_unset=True)
    repo = LoginRepository()

    logger.debug(f"Updating login with ID {id} and data: {login_dict}")

    result = await repo.update_login(id, login_dict)
    if result:
        logger.info("Login updated successfully.")
        return req
    else:
        logger.error("Problem encountered while updating login profile.")
        return JSONResponse(content={'message': 'Update login profile problem encountered'}, status_code=500)


@router.get("/login/list/all")
async def list_login():
    repo = LoginRepository()

    logger.debug("Fetching all login records.")

    result = await repo.get_all_login()
    data = jsonable_encoder(result)

    logger.info(f"Fetched {len(data)} login records.")
    return data


@router.get("/login/list/records")
async def list_login_records():
    repo = LoginRepository()

    logger.debug("Fetching all login records for summary.")

    login_data = await repo.get_all_login()
    result = await asyncio.gather(count_login(login_data), build_user_list(login_data))

    data = jsonable_encoder(result[1])
    logger.info(f"Counted {result[0]} login records and built user list.")

    return {'num_rec': result[0], 'user_list': data}