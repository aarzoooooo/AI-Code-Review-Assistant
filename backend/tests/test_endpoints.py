import pytest


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Backend Running" in r.json()["message"]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_review_success_returns_structured_review(client, fake_gemini, valid_payload):
    fake_gemini()
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 200
    body = r.json()
    assert body["cached"] is False
    review = body["review"]
    assert review["rating"] == 7
    assert review["bugs"][0] == {"description": "Off-by-one in loop", "line": 3}
    assert set(review) == {"rating", "summary", "bugs", "optimizations", "best_practices", "suggestions"}


@pytest.mark.parametrize("language", ["Python", "Java", "C++", "JavaScript", "C"])
def test_all_five_languages_accepted(client, fake_gemini, language):
    fake_gemini()
    r = client.post("/review", json={"language": language, "code": "x"})
    assert r.status_code == 200


def test_rating_is_clamped_to_1_10(client, fake_gemini, valid_payload):
    import json
    from tests.conftest import GOOD_REVIEW

    fake_gemini([json.dumps({**GOOD_REVIEW, "rating": 42})])
    assert client.post("/review", json=valid_payload).json()["review"]["rating"] == 10


def test_unknown_route_404(client):
    assert client.get("/nope").status_code == 404


def test_models_endpoint_not_exposed(client):
    assert client.get("/models").status_code == 404


def test_cors_allows_configured_origin(client):
    r = client.options(
        "/review",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5500"


def test_cors_blocks_unknown_origin(client):
    r = client.options(
        "/review",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in r.headers
