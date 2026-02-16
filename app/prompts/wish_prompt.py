"""
Prompt templates for Wish (Lì Xì) generation.

Design principles:
  • System prompt defines persona + constraints
  • User prompt injects dynamic parameters
  • Output is plain text (single wish sentence)
"""

from __future__ import annotations

from app.models.schemas import LixiType

# ── Mệnh giá → Mô tả giọng điệu ────────────────────────────

_TIER_GUIDANCE: dict[LixiType, str] = {
    LixiType.K50: (
        "Mệnh giá 50.000đ – nhỏ nhưng ý nghĩa. "
        "Giọng nhẹ nhàng, ấm áp, mang ý bình an, khởi đầu may mắn."
    ),
    LixiType.K100: (
        "Mệnh giá 100.000đ – vừa phải, tốt lành. "
        "Giọng vui vẻ, trang trọng, chúc an khang thịnh vượng."
    ),
    LixiType.K200: (
        "Mệnh giá 200.000đ – khá may mắn. "
        "Giọng phấn khởi, chúc tài lộc hanh thông, công việc thuận buồm."
    ),
    LixiType.K500: (
        "Mệnh giá 500.000đ – rất may mắn! "
        "Giọng hào sảng, đại phát tài, phú quý song toàn."
    ),
    LixiType.SPECIAL: (
        "Mệnh giá ĐẶC BIỆT – jackpot siêu hiếm! "
        "Giọng phấn khích, chúc mừng đặc biệt, siêu may mắn, rực rỡ cả năm."
    ),
}

WISH_SYSTEM_PROMPT = """\
Bạn là một nhà thư pháp Việt Nam chuyên viết lời chúc Tết Nguyên Đán.

QUY TẮC BẮT BUỘC:
- Viết ĐÚNG 1 câu chúc duy nhất, tối đa 40 từ.
- Sử dụng tiếng Việt có dấu, văn phong trang nhã nhưng gần gũi.
- Có thể thêm 1-2 emoji phù hợp ở cuối câu.
- KHÔNG dùng markdown, KHÔNG xuống dòng, KHÔNG giải thích thêm.
- Mỗi lời chúc phải KHÁC BIỆT, sáng tạo, không lặp lại khuôn mẫu.
- Nếu có tên người nhận, hãy gọi tên thân mật ở đầu câu.
"""


def build_wish_prompt(lixi_type: LixiType, user_name: str | None = None) -> str:
    """Build the user message for wish generation."""
    parts = [f"Mệnh giá: {_TIER_GUIDANCE[lixi_type]}"]

    if user_name:
        parts.append(f"Người nhận tên: {user_name}")

    parts.append("Hãy viết 1 câu chúc Tết:")
    return "\n".join(parts)
