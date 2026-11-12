FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py schemas.py cache.py gemini_service.py main.py ./

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Render injects $PORT; default to 8000 locally.
# --proxy-headers makes the real client IP visible to the rate limiter.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
