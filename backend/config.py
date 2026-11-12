"""Central configuration, read from environment variables (see .env.example)."""
import os

from dotenv import load_dotenv

load_dotenv()


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Tried in order; the next model is used if one is unavailable or returns nothing.
GEMINI_MODELS = _csv(os.getenv("GEMINI_MODELS", "gemini-3.6-flash"))

MAX_RETRIES_PER_MODEL = int(os.getenv("MAX_RETRIES_PER_MODEL", "2"))
RETRYABLE_STATUS_CODES = {429, 500, 503}

# Origins allowed to call the API from a browser (set to your Vercel URL in production).
ALLOWED_ORIGINS = _csv(
    os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500")
)

RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "256"))
