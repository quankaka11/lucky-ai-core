"""
FastAPI application factory.

Creates and configures the app with CORS, rate limiting, and routes.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.routes import limiter, router


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    settings = get_settings()

    # ── Logging ───────────────────────────────────────────────
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── App ───────────────────────────────────────────────────
    app = FastAPI(
        title="Lucky Envelope AI",
        description="AI backend for Tết wish & fortune generation",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
    )

    # ── CORS ──────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Rate limiting ─────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Routes ────────────────────────────────────────────────
    app.include_router(router)

    return app


app = create_app()
