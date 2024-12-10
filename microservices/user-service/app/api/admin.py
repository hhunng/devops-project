from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.request.admin import AdminReq
from models.data.nsms import Admin, Login
from repository.admin import AdminRepository, AdminLoginRepository
from repository.billing import BillingAdminRepository
from config.db.gino_db import db

from services.admin import process_billing, extract_enc_admin_profile
import asyncio
import logging.config

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/admin/add")
async def add_admin(req: AdminReq):
    admin_dict = req.dict(exclude_unset=True)
    repo = AdminRepository()

    logger.debug(f"Adding admin with data: {admin_dict}")

    result = await repo.insert_admin(admin_dict)
    if result:
        logger.info("Admin added successfully.")
        return req
    else:
        logger.error("Problem encountered while adding admin.")
        return JSONResponse(content={'message': 'Update admin profile problem encountered'}, status_code=500)


@router.post("/admin/login/list")
async def list_admin_login():
    repo = AdminLoginRepository()

    logger.debug("Fetching admin login details.")

    result = await repo.join_login_admin()
    logger.info(f"Fetched {len(result)} admin login records.")
    return result


@router.get("/admin/billing/all")
async def list_admin_with_billing():
    repo = BillingAdminRepository()

    logger.debug("Fetching admins with billing information.")

    result = await repo.join_admin_billing()
    data = await process_billing(result)

    logger.info("Processed billing information for admins.")
    return jsonable_encoder(data)


@router.get("/admin/login/list/enc")
async def generate_encrypted_profile():
    repo = AdminLoginRepository()

    logger.debug("Generating encrypted profiles for admin logins.")

    result = await repo.join_login_admin()
    encoded_data = await asyncio.gather(*(extract_enc_admin_profile(rec) for rec in result))

    logger.info("Encrypted profiles generated successfully.")
    return {"message": "done"}