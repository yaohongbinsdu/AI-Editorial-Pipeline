import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select

from app.api.deps import DBSession
from app.models.rss_source import RSSSource

router = APIRouter()


class SourceCreate(BaseModel):
    url: str
    name: str
    category: str
    fetch_interval_minutes: int = 60


class SourceUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    enabled: bool | None = None
    fetch_interval_minutes: int | None = None


class SourceResponse(BaseModel):
    id: str
    url: str
    name: str
    category: str
    enabled: bool
    fetch_interval_minutes: int
    last_fetched_at: str | None
    consecutive_failures: int

    model_config = {"from_attributes": True}


@router.get("/sources")
async def list_sources(db: DBSession):
    result = await db.execute(select(RSSSource).order_by(RSSSource.name))
    sources = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "url": s.url,
            "name": s.name,
            "category": s.category,
            "enabled": s.enabled,
            "fetch_interval_minutes": s.fetch_interval_minutes,
            "last_fetched_at": s.last_fetched_at.isoformat() if s.last_fetched_at else None,
            "consecutive_failures": s.consecutive_failures,
        }
        for s in sources
    ]


@router.post("/sources", status_code=201)
async def create_source(body: SourceCreate, db: DBSession):
    existing = await db.execute(select(RSSSource).where(RSSSource.url == body.url))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Source URL already exists")

    source = RSSSource(
        url=body.url,
        name=body.name,
        category=body.category,
        fetch_interval_minutes=body.fetch_interval_minutes,
    )
    db.add(source)
    await db.flush()
    return {
        "id": str(source.id),
        "url": source.url,
        "name": source.name,
        "category": source.category,
        "enabled": source.enabled,
        "fetch_interval_minutes": source.fetch_interval_minutes,
        "last_fetched_at": None,
        "consecutive_failures": 0,
    }


@router.patch("/sources/{source_id}")
async def update_source(source_id: str, body: SourceUpdate, db: DBSession):
    source = await db.get(RSSSource, uuid.UUID(source_id))
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    if body.name is not None:
        source.name = body.name
    if body.category is not None:
        source.category = body.category
    if body.enabled is not None:
        source.enabled = body.enabled
    if body.fetch_interval_minutes is not None:
        source.fetch_interval_minutes = body.fetch_interval_minutes

    await db.flush()
    return {
        "id": str(source.id),
        "url": source.url,
        "name": source.name,
        "category": source.category,
        "enabled": source.enabled,
        "fetch_interval_minutes": source.fetch_interval_minutes,
        "last_fetched_at": source.last_fetched_at.isoformat() if source.last_fetched_at else None,
        "consecutive_failures": source.consecutive_failures,
    }


@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(source_id: str, db: DBSession):
    source = await db.get(RSSSource, uuid.UUID(source_id))
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    await db.delete(source)
    return None
