"""
Azure OpenAI service – single call function with retry & fallback.

This module is the ONLY place that interacts with the OpenAI SDK.
All other modules use the high-level `generate_wish` / `generate_fortune`.
"""

from __future__ import annotations

import json
import logging
import time

from openai import AzureOpenAI, APIError, APITimeoutError, RateLimitError

from app.config import get_settings
from app.models.schemas import (
    FortuneData,
    FortuneMode,
    FortuneResponse,
    LixiType,
    WishResponse,
)
from app.prompts.fortune_prompt import FORTUNE_SYSTEM_PROMPT, build_fortune_prompt
from app.prompts.wish_prompt import WISH_SYSTEM_PROMPT, build_wish_prompt

logger = logging.getLogger(__name__)

# ── Fallback data ─────────────────────────────────────────────

_FALLBACK_WISHES: dict[LixiType, list[str]] = {
    LixiType.K50: [
        "Chúc năm mới nhẹ nhàng, tiền vào đều đều 🍀",
        "Năm mới bình an, túi luôn rủng rỉnh 💚",
    ],
    LixiType.K100: [
        "Chúc bạn an khang, tài lộc khởi sắc 💰",
        "Năm mới vạn sự như ý, tiền tài dồi dào 🎋",
    ],
    LixiType.K200: [
        "Công việc hanh thông, lộc đến bất ngờ ✨",
        "Tài lộc phơi phới, vạn sự hanh thông 🌟",
    ],
    LixiType.K500: [
        "Phát tài phát lộc, tiền rủng rỉnh cả năm 🧧",
        "Đại phát, đại lộc – năm nay là năm của bạn! 🎊",
    ],
    LixiType.SPECIAL: [
        "WOW! Siêu may mắn – năm nay chắc chắn bứt phá 🎆",
        "JACKPOT! Vận may đỉnh cao, cả năm rực rỡ 🌈✨",
    ],
}

_FALLBACK_FORTUNE = FortuneData(
    title="Vạn Sự Như Ý",
    rating=4,
    summary="Năm mới nhiều thuận lợi, mọi việc hanh thông.",
    detail="Vận thế đang lên, các kế hoạch sẽ được triển khai suôn sẻ. "
           "Quý nhân sẽ xuất hiện đúng lúc để hỗ trợ bạn.",
    advice="Kiên trì với mục tiêu đã đặt ra, đừng dao động.",
    lucky_element="Màu đỏ, số 8, hướng Đông",
    emoji="🎊",
)


# ── Client factory ────────────────────────────────────────────
def _get_client() -> AzureOpenAI:
    "Khởi tạo client"
    settings = get_settings()
    return AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version
    )
def _chat(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.85,
    max_tokens: int = 500,
) -> str:
    """
    Low-level chat completion call with basic retry.

    Retries once on timeout/rate-limit, then raises.
    """
    settings = get_settings()
    client = _get_client()

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from Azure OpenAI")
            return content.strip()

        except (APITimeoutError, RateLimitError) as exc:
            if attempt == 0:
                wait = 2.0
                logger.warning(
                    "Azure OpenAI %s (attempt %d), retrying in %.1fs...",
                    type(exc).__name__, attempt + 1, wait,
                )
                time.sleep(wait)
            else:
                raise

    # Unreachable, but satisfies type checker
    raise RuntimeError("Exhausted retries")


# ── Public API ────────────────────────────────────────────────

def generate_wish(
    lixi_type: LixiType,
    user_name: str | None = None,
) -> WishResponse:
    """
    Generate a Tết wish for the given denomination.

    Falls back to mock data if AI fails.
    """
    try:
        user_prompt = build_wish_prompt(lixi_type, user_name)
        wish_text = _chat(
            WISH_SYSTEM_PROMPT,
            user_prompt,
            temperature=0.9,
            max_tokens=120,
        )
        # Strip any accidental quotes
        wish_text = wish_text.strip('"').strip("'")
        logger.info("AI wish generated for %s", lixi_type.value)

    except Exception:
        logger.exception("AI wish generation failed, using fallback")
        import random
        wish_text = random.choice(_FALLBACK_WISHES[lixi_type])

    return WishResponse(wish_text=wish_text, lixi_type=lixi_type)


def generate_fortune(
    mode: FortuneMode,
    user_name: str | None = None,
) -> FortuneResponse:
    """
    Generate a fortune reading for the given mode.

    Falls back to mock data if AI fails or returns invalid JSON.
    """
    fortune_data: FortuneData

    try:
        user_prompt = build_fortune_prompt(mode, user_name)
        raw = _chat(
            FORTUNE_SYSTEM_PROMPT,
            user_prompt,
            temperature=0.85,
            max_tokens=500,
        )

        # Clean potential markdown fences
        cleaned = raw
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        fortune_data = FortuneData.model_validate(parsed)
        logger.info("AI fortune generated: %s", fortune_data.title)

    except Exception:
        logger.exception("AI fortune generation failed, using fallback")
        fortune_data = _FALLBACK_FORTUNE

    return FortuneResponse(
        fortune=fortune_data,
        mode=mode,
        drawn_at=int(time.time() * 1000),
    )
