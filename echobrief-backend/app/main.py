import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1.articles import router as articles_router
from app.api.v1.auth import router as auth_router
from app.api.v1.podcasts import router as podcasts_router
from app.api.v1.sources import router as sources_router
from app.api.v1.system import router as system_router
from app.api.v1.topics import router as topics_router
from app.api.v1.users import router as users_router
from app.core.database import engine

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="EchoBrief API",
    description="API for generating podcast briefs from news articles",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(topics_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(articles_router, prefix="/api/v1")
app.include_router(podcasts_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

# Mount static files for audio serving
audio_dir = os.path.join(os.path.dirname(__file__), "..", "audio")
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")


@app.get("/")
async def root():
    return {"message": "Welcome to EchoBrief!"}


@app.get("/health/db")
async def health_db():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
