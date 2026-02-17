# ============================================================
# AI-Core Backend – Python 3.11
# ============================================================
FROM python:3.11-slim

# Không tạo file .pyc, flush output ngay lập tức
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài dependencies trước (tận dụng Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Port mặc định (có thể override bằng env var PORT)
EXPOSE 8000

# Health check – kiểm tra API có sống không
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Khởi động ứng dụng
CMD ["python", "start.py"]
