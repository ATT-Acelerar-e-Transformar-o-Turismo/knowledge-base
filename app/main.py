import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import connect_to_mongo, close_mongo_connection
from app.routes import blog_routes, file_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Knowledge Base API",
    description="API for blog posts and knowledge management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = os.getenv("ORIGINS", "localhost").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(blog_routes.router)
app.include_router(file_routes.router)


@app.get("/")
def read_root():
    return {"message": "Knowledge Base API - Blog and File Management"}
