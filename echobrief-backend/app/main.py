import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.admin import router as admin_router
from app.api.v1.articles import router as articles_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.podcasts import router as podcasts_router
from app.api.v1.sources import router as sources_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.system import router as system_router
from app.api.v1.topics import router as topics_router
from app.api.v1.users import router as users_router
from app.core.database import engine
from app.core.middleware import RateLimitMiddleware

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

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)


origins = [
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(topics_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(articles_router, prefix="/api/v1")
app.include_router(podcasts_router, prefix="/api/v1")
app.include_router(subscriptions_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

# Mount static files for audio serving
audio_dir = os.path.join(os.path.dirname(__file__), "..", "audio")
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

# Mount static files for avatar serving
avatar_dir = os.path.join(os.path.dirname(__file__), "..", "avatar")
app.mount("/avatars", StaticFiles(directory=avatar_dir), name="avatars")


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
