import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import db_manager
from app.routes import blog_routes, file_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_manager.connect()
    yield
    await db_manager.disconnect()


app = FastAPI(
    title="Knowledge Base API",
    description="API for blog posts and knowledge management",
    version="1.0.0",
    lifespan=lifespan
)

origins = settings.ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog_routes.router)
app.include_router(file_routes.router)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Knowledge Base API - Blog and File Management"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "knowledge-base"}
