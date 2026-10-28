"""FastAPI Application entrypoint for F1 Race Intelligence Dashboard.

Provides motorsport analytics, telemetry endpoints, and historical query interfaces
for Formula 1 seasons 2010 through 2026.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base
import app.models  # Ensure all models are registered
from app.api.routes import router

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="F1 Race Intelligence API",
    description=(
        "Production analytics backend for Formula 1 Race Intelligence Dashboard (2010–2026). "
        "Provides validated historical analytics, constructor progression, driver head-to-heads, "
        "circuit statistics, reliability telemetry, and data exploration tools."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "title": "F1 Race Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "seasons_covered": "2010-2026",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )
