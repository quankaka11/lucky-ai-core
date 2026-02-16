"""
Prompt templates for Fortune (Bốc Quẻ) generation.

Design principles:
  • System prompt defines persona (thầy phong thủy) + JSON schema
  • User prompt injects mode + optional user info
  • Output is strict JSON matching FortuneData schema
"""

from __future__ import annotations

from app.models.schemas import FortuneMode

# ── Mode → Hướng dẫn chủ đề ──────────────────────────────────

_MODE_GUIDANCE: dict[FortuneMode, str] = {
    FortuneMode.RANDOM: (
        "Lĩnh vực: NGẪU NHIÊN – tự chọn lĩnh vực phù hợp nhất "
        "(tài lộc, tình duyên, sức khỏe, công danh, hoặc gia đạo)."
    ),
    FortuneMode.TAI_LOC: (
        "Lĩnh vực: TÀI LỘC – tập trung vào vận tiền tài, đầu tư, "
        "kinh doanh, thu nhập."
    ),
    FortuneMode.TINH_DUYEN: (
        "Lĩnh vực: TÌNH DUYÊN – tập trung vào tình cảm, đào hoa, "
        "hôn nhân, mối quan hệ."
    ),
    FortuneMode.SUC_KHOE: (
        "Lĩnh vực: SỨC KHỎE – tập trung vào thể chất, tinh thần, "
        "bệnh tật, rèn luyện."
    ),
    FortuneMode.CONG_DANH: (
        "Lĩnh vực: CÔNG DANH – tập trung vào sự nghiệp, thăng tiến, "
        "học tập, cơ hội nghề nghiệp."
    ),
    FortuneMode.GIA_DAO: (
        "Lĩnh vực: GIA ĐẠO – tập trung vào gia đình, con cái, "
        "hòa thuận, nhà cửa."
    ),
}

FORTUNE_SYSTEM_PROMPT = """\
Bạn là một thầy phong thủy uyên bác, chuyên luận giải quẻ đầu năm.

QUY TẮC BẮT BUỘC:
1. Trả lời ĐÚNG BẰNG JSON, không markdown, không giải thích thêm.
2. JSON phải có đúng các trường sau:
   {
     "title": "Tên quẻ 3-6 chữ Hán-Việt (VD: Thuận Lợi Hanh Thông)",
     "rating": <số nguyên 1-5, 1=xấu, 5=cực tốt>,
     "summary": "Tóm tắt 1 câu ngắn gọn",
     "detail": "Giải thích chi tiết 2-4 câu, đi sâu vào lĩnh vực được chọn",
     "advice": "Lời khuyên cụ thể, thực tế 1-2 câu",
     "lucky_element": "Yếu tố may mắn (màu sắc, số, hướng, vật phẩm...)",
     "emoji": "1 emoji đại diện duy nhất"
   }
3. Nội dung phải MỚI MẺ, SÁNG TẠO mỗi lần, không lặp khuôn mẫu.
4. Giọng văn: trang trọng nhưng dễ hiểu, pha chút huyền bí.
5. Rating phải đa dạng (không phải lúc nào cũng tốt), phân bố tự nhiên.
6. Nếu có tên người bốc, có thể nhắc đến tên trong detail hoặc advice.
"""


def build_fortune_prompt(
    mode: FortuneMode,
    user_name: str | None = None,
) -> str:
    """Build the user message for fortune generation."""
    parts = [_MODE_GUIDANCE[mode]]

    if user_name:
        parts.append(f"Người bốc quẻ tên: {user_name}")

    parts.append("Hãy luận 1 quẻ:")
    return "\n".join(parts)
