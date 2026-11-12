import json
import os

# Must be set before the app is imported: config reads the environment at import time.
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5500"
os.environ["RATE_LIMIT"] = "3/minute"

import pytest
from fastapi.testclient import TestClient
from google.genai import errors as genai_errors

import cache
import gemini_service
from main import app, limiter

GOOD_REVIEW = {
    "rating": 7,
    "summary": "Mostly fine.",
    "bugs": [{"description": "Off-by-one in loop", "line": 3}],
    "optimizations": [],
    "best_practices": [{"description": "Add a docstring", "line": None}],
    "suggestions": ["Add tests"],
}


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeGemini:
    """Stands in for genai.Client. `outcomes` is consumed one item per call:
    an Exception is raised, anything else is returned as the response text."""

    def __init__(self, outcomes=None):
        self.outcomes = list(outcomes) if outcomes is not None else [json.dumps(GOOD_REVIEW)] * 50
        self.calls = 0
        self.models = self  # client.models.generate_content(...)

    def generate_content(self, **kwargs):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(outcome)


def api_error(code: int) -> genai_errors.APIError:
    return genai_errors.APIError(code, {"error": {"message": f"fake {code}", "status": "X"}})


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    cache.clear()
    limiter.reset()
    monkeypatch.setattr(gemini_service.time, "sleep", lambda s: None)  # no real backoff waits
    yield


@pytest.fixture
def fake_gemini(monkeypatch):
    def install(outcomes=None) -> FakeGemini:
        fake = FakeGemini(outcomes)
        monkeypatch.setattr(gemini_service, "get_client", lambda: fake)
        return fake

    return install


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_payload():
    return {"language": "Python", "code": "for i in range(3):\n    print(i)"}
