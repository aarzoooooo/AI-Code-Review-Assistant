"""Pydantic models: request validation and the structured review returned by the API."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator

SUPPORTED_LANGUAGES = ("Python", "Java", "C++", "JavaScript", "C")
MAX_CODE_CHARS = 10_000


class CodeRequest(BaseModel):
    language: Literal["Python", "Java", "C++", "JavaScript", "C"]
    code: str = Field(min_length=1, max_length=MAX_CODE_CHARS)

    @field_validator("code")
    @classmethod
    def code_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("code must not be blank")
        return value


class Finding(BaseModel):
    description: str
    line: int | None = None  # line number in the submitted code, if applicable


class ReviewResult(BaseModel):
    """Also used as the response schema we ask Gemini to follow."""

    rating: int  # 1-10 overall score
    summary: str
    bugs: list[Finding]
    optimizations: list[Finding]
    best_practices: list[Finding]
    suggestions: list[str]


class ReviewResponse(BaseModel):
    review: ReviewResult
    cached: bool = False
