from fastapi import APIRouter

from app.api.deps import DBSession

router = APIRouter()


@router.get("/sources")
async def list_sources(db: DBSession):
    return []


@router.post("/sources", status_code=201)
async def create_source(db: DBSession):
    return {}


@router.patch("/sources/{source_id}")
async def update_source(source_id: str, db: DBSession):
    return {}


@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(source_id: str, db: DBSession):
    return None
