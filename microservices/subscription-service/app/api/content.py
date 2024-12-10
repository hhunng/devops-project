from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from models.request.content import ContentReq
from models.data.nsms import Content, Publication
from repository.content import ContentRepository
from config.db.gino_db import db
import logging.config

logging.config.fileConfig('../logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/content/add")
async def add_content(req: ContentReq):
    content_dict = req.dict(exclude_unset=True)
    repo = ContentRepository()

    logger.debug(f"Adding content with data: {content_dict}")

    result = await repo.insert_content(content_dict)
    if result:
        logger.info("Content added successfully.")
        return req
    else:
        logger.error("Problem encountered while adding content.")
        return JSONResponse(content={'message': 'Update content problem encountered'}, status_code=500)


@router.get("/content/list")
async def list_content():
    repo = ContentRepository()

    logger.debug("Fetching all content.")

    result = await repo.get_all_content()
    logger.info(f"Fetched {len(result)} content items.")

    return result