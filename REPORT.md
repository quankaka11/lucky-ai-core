# 🎯 AI-Core: Báo Cáo Triển Khai

> **Dự án:** Lucky Envelope – AI Backend  
> **Ngày tạo:** 2026-02-16  
> **Tech stack:** Python 3.11+ · FastAPI · Azure OpenAI · Pydantic  

---

## 1. Tổng Quan Kiến Trúc

```
lucky-lucky/
├── lucky-envelope-main/    ← Frontend (Vite + React)
│   └── src/lib/
│       ├── lixi-config.ts     → gọi POST /api/wish
│       └── fortune-config.ts  → gọi POST /api/fortune
│
└── ai-core/                ← Backend (FastAPI) ★ MỚI
    ├── app/
    │   ├── main.py            → App factory, CORS, rate limit
    │   ├── config.py          → Env vars (pydantic-settings)
    │   ├── routes.py          → API endpoints
    │   ├── models/
    │   │   └── schemas.py     → Request/Response Pydantic models
    │   ├── prompts/
    │   │   ├── wish_prompt.py    → Prompt templates cho lời chúc
    │   │   └── fortune_prompt.py → Prompt templates cho bốc quẻ
    │   └── services/
    │       └── ai_service.py  → Azure OpenAI client + fallback
    ├── .env.example
    ├── .gitignore
    └── requirements.txt
```

**Nguyên tắc thiết kế:**
- **Separation of concerns**: Prompt / Service / Route / Schema tách riêng
- **Fallback-first**: Nếu AI lỗi → tự động dùng mock data, app không bao giờ crash
- **API key an toàn**: Key chỉ tồn tại ở server, không bao giờ gửi lên frontend

---

## 2. API Endpoints

### `POST /api/wish` – Tạo lời chúc Tết

**Request:**
```json
{
  "lixi_type": "500k",
  "user_name": "Minh"       // tuỳ chọn
}
```

**Response:**
```json
{
  "wish_text": "Chúc Minh năm mới đại phát tài, tiền vào ào ào như thác đổ 🧧🎊",
  "lixi_type": "500k"
}
```

### `POST /api/fortune` – Bốc quẻ AI

**Request:**
```json
{
  "mode": "tai_loc",
  "user_name": "Lan"        // tuỳ chọn
}
```

**Response:**
```json
{
  "fortune": {
    "title": "Kim Ngọc Mãn Đường",
    "rating": 5,
    "summary": "Vận tài lộc đỉnh cao, mọi nỗ lực đều được đền đáp.",
    "detail": "Lan sẽ có cơ hội tài chính lớn trong thời gian tới...",
    "advice": "Mạnh dạn đầu tư nhưng vẫn giữ quỹ dự phòng.",
    "lucky_element": "Màu đỏ vàng, số 88, hướng Đông",
    "emoji": "👑"
  },
  "mode": "tai_loc",
  "drawn_at": 1739692800000
}
```

### `GET /api/health` – Health check

```json
{ "status": "ok", "service": "ai-core" }
```

---

## 3. Prompt Design

### 3.1 Lời chúc (Wish)

| Thành phần | Vai trò |
|---|---|
| **System prompt** | Persona "nhà thư pháp", ràng buộc: 1 câu, ≤40 từ, tiếng Việt, có emoji |
| **Tier guidance** | Mỗi mệnh giá có hướng dẫn giọng điệu riêng (50k nhẹ nhàng → special phấn khích) |
| **User name** | Nếu có → AI gọi tên thân mật đầu câu |

### 3.2 Quẻ (Fortune)

| Thành phần | Vai trò |
|---|---|
| **System prompt** | Persona "thầy phong thủy", yêu cầu trả JSON chính xác schema |
| **Mode guidance** | Mỗi mode có context riêng (tài lộc → tiền tài, tình duyên → tình cảm...) |
| **JSON schema** | Ép AI trả đúng cấu trúc `FortuneData`, validate bằng Pydantic |

---

## 4. Cơ Chế An Toàn

```
Request → Rate Limit → Route → AI Service → Azure OpenAI
                                    ↓ (lỗi)
                               Fallback Mock Data
```

| Rủi ro | Giải pháp |
|---|---|
| API key bị lộ | Key chỉ ở `.env` server-side, CORS chặn origin lạ |
| Azure OpenAI timeout | Retry 1 lần sau 2 giây |
| Azure OpenAI rate limit | Retry + slowapi rate limit phía server (30 req/min/IP) |
| AI trả JSON sai format | Pydantic validation → fallback mock data |
| AI trả markdown wrapper | Auto-strip ````json...``` fences trước khi parse |
| App bị spam | slowapi rate limiting per IP |

---

## 5. Hướng Dẫn Chạy

### 5.1 Cài đặt

```bash
cd ai-core

# Tạo virtual environment
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt
```

### 5.2 Cấu hình

```bash
# Copy file env mẫu
cp .env.example .env

# Sửa .env, điền Azure OpenAI credentials:
# AZURE_OPENAI_API_KEY=sk-...
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### 5.3 Chạy server

```bash
uvicorn app.main:app --reload --port 8000
```

Server chạy tại `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

### 5.4 Test nhanh

```bash
# Health check
curl http://localhost:8000/api/health

# Tạo lời chúc
curl -X POST http://localhost:8000/api/wish \
  -H "Content-Type: application/json" \
  -d '{"lixi_type": "500k", "user_name": "Minh"}'

# Bốc quẻ
curl -X POST http://localhost:8000/api/fortune \
  -H "Content-Type: application/json" \
  -d '{"mode": "tai_loc"}'
```

---

## 6. Tích Hợp Frontend (Bước Tiếp Theo)

Khi AI backend đã chạy ổn, chỉ cần sửa 2 hàm ở frontend:

### `lixi-config.ts` → `getWish()`
```typescript
export async function getWish(imageType: LixiType): Promise<string> {
  try {
    const res = await fetch("http://localhost:8000/api/wish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lixi_type: imageType }),
    });
    const data = await res.json();
    return data.wish_text;
  } catch {
    // Fallback to mock
    return randomItem(MOCK_WISH[imageType]);
  }
}
```

### `fortune-config.ts` → `getFortune()`
```typescript
export async function getFortune(mode: FortuneMode): Promise<FortuneResult> {
  try {
    const res = await fetch("http://localhost:8000/api/fortune", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    });
    const data = await res.json();
    return {
      fortune: {
        id: `ai-${Date.now()}`,
        category: mode === "random" ? "tai_loc" : mode,
        ...data.fortune,
        luckyElement: data.fortune.lucky_element,
      },
      drawnAt: data.drawn_at,
    };
  } catch {
    return { fortune: randomFortune(mode), drawnAt: Date.now() };
  }
}
```

---

## 7. Cấu Trúc File

| File | Dòng | Mục đích |
|---|---|---|
| `app/config.py` | ~42 | Load & validate env vars |
| `app/main.py` | ~55 | App factory, middleware |
| `app/routes.py` | ~55 | API endpoints |
| `app/models/schemas.py` | ~75 | Pydantic request/response |
| `app/prompts/wish_prompt.py` | ~50 | Prompt cho lời chúc |
| `app/prompts/fortune_prompt.py` | ~60 | Prompt cho bốc quẻ |
| `app/services/ai_service.py` | ~170 | OpenAI client + fallback |
| **Tổng** | **~507** | |

---

## 8. Lưu Ý Quan Trọng

1. **Không commit `.env`** – file này chứa API key, đã có trong `.gitignore`
2. **Dùng GPT-4o mini** – rẻ hơn 10x so với GPT-4o, đủ chất lượng cho use case này
3. **Latency**: AI response mất ~1-3 giây. Frontend đã có animation chờ nên UX sẽ mượt
4. **Chi phí ước tính**: GPT-4o mini ~$0.15/1M input tokens → ~10.000 lần bốc ≈ $0.15
5. **CORS**: Nhớ cập nhật `ALLOWED_ORIGINS` khi deploy production
