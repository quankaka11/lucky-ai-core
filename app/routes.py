"""
API routes – /api/wish and /api/fortune.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.models.schemas import (
    FortuneRequest,
    FortuneResponse,
    HealthResponse,
    WishRequest,
    WishResponse,
)
from app.services.ai_service import generate_fortune, generate_wish

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["AI"])

limiter = Limiter(key_func=get_remote_address)


# ── Health ────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple liveness probe."""
    return HealthResponse()


# ── Wish ──────────────────────────────────────────────────────

@limiter.limit(lambda: f"{get_settings().rate_limit_per_minute}/minute")
@router.post("/wish", response_model=WishResponse)
async def create_wish(request: Request, body: WishRequest):
    """
    Generate a Tết wish for the given lì xì denomination.

    - **lixi_type**: 50k | 100k | 200k | 500k | special
    - **user_name**: Optional recipient name for personalization
    """
    logger.info("Wish request: type=%s, user=%s", body.lixi_type, body.user_name)
    return generate_wish(body.lixi_type, body.user_name)


# ── Fortune ───────────────────────────────────────────────────

@limiter.limit(lambda: f"{get_settings().rate_limit_per_minute}/minute")
@router.post("/fortune", response_model=FortuneResponse)
async def create_fortune(request: Request, body: FortuneRequest):
    """
    Generate a fortune reading (bốc quẻ) for the given mode.

    - **mode**: random | tai_loc | tinh_duyen | suc_khoe | cong_danh | gia_dao
    - **user_name**: Optional name for personalization
    """
    logger.info("Fortune request: mode=%s, user=%s", body.mode, body.user_name)
    return generate_fortune(body.mode, body.user_name)
