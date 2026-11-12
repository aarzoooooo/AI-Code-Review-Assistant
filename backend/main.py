import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import cache
import config
import gemini_service
from schemas import CodeRequest, ReviewResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code-review")

app = FastAPI(title="AI Code Review API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Keyed by client IP. In production uvicorn runs with --proxy-headers so this
# is the real client IP rather than the platform's proxy.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please wait a moment and try again."},
        headers={"Retry-After": "60"},
    )


@app.exception_handler(gemini_service.ReviewError)
async def review_error_handler(request: Request, exc: gemini_service.ReviewError):
    logger.error("Review failed: %s", exc)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.public_message})


@app.get("/")
def home():
    return {"message": "AI Code Review Assistant Backend Running!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResponse)
@limiter.limit(config.RATE_LIMIT)
def review_code(request: Request, body: CodeRequest):
    key = cache.make_key(body.language, body.code)

    cached = cache.get(key)
    if cached is not None:
        return ReviewResponse(review=cached, cached=True)

    result = gemini_service.generate_review(body.language, body.code)
    cache.set(key, result)  # only successful reviews are cached
    return ReviewResponse(review=result, cached=False)
