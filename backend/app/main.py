from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import articles, categories, clusters, dashboard, pipeline, sources
from app.models import engine
from app import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    scheduler.start()
    yield
    scheduler.stop()
    await engine.dispose()


app = FastAPI(
    title="AI Editorial Pipeline",
    description="全自动AI编辑部 — 面向投资者的新闻聚合与智能分析平台",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(articles.router, prefix="/api/v1", tags=["Articles"])
app.include_router(clusters.router, prefix="/api/v1", tags=["Clusters"])
app.include_router(categories.router, prefix="/api/v1", tags=["Categories"])
app.include_router(sources.router, prefix="/api/v1", tags=["Sources"])
app.include_router(pipeline.router, prefix="/api/v1", tags=["Pipeline"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
