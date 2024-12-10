from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models.request.vendor import VendorReq
from models.data.nsms import Vendor, Login
from repository.vendor import VendorRepository
from config.db.gino_db import db
import logging.config

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/vendor/add")
async def add_vendor(req: VendorReq):
    vendor_dict = req.dict(exclude_unset=True)
    repo = VendorRepository()

    logger.debug(f"Adding vendor with data: {vendor_dict}")

    result = await repo.insert_vendor(vendor_dict)
    if result:
        logger.info("Vendor added successfully.")
        return req
    else:
        logger.error("Problem encountered while adding vendor.")
        return JSONResponse(content={'message': 'Update vendor profile problem encountered'}, status_code=500)


@router.get("/vendor/list")
async def list_vendor():
    repo = VendorRepository()

    logger.debug("Fetching all vendors.")

    result = await repo.get_all_vendor()
    logger.info(f"Fetched {len(result)} vendors.")

    return result