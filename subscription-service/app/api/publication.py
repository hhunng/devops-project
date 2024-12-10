from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models.request.publication import PublicationReq
from models.data.nsms import Publication, Messenger
from repository.publication import PublicationRepository
from config.db.gino_db import db
import logging.config

router = APIRouter()


@router.post("/publication/add")
async def add_publication(req: PublicationReq):
    publication_dict = req.dict(exclude_unset=True)
    repo = PublicationRepository()

    logger.debug(f"Adding publication with data: {publication_dict}")

    result = await repo.insert_publication(publication_dict)
    if result:
        logger.info("Publication added successfully.")
        return req
    else:
        logger.error("Problem encountered while adding publication.")
        return JSONResponse(content={'message': 'Update publication problem encountered'}, status_code=500)


@router.get("/publication/list")
async def list_publication():
    repo = PublicationRepository()

    logger.debug("Fetching all publications.")

    result = await repo.get_all_publication()
    logger.info(f"Fetched {len(result)} publication items.")

    return result