import json

from tests.conftest import GOOD_REVIEW, api_error


def test_identical_request_is_served_from_cache(client, fake_gemini, valid_payload):
    fake = fake_gemini()
    first = client.post("/review", json=valid_payload).json()
    second = client.post("/review", json=valid_payload).json()
    assert first["cached"] is False
    assert second["cached"] is True
    assert second["review"] == first["review"]
    assert fake.calls == 1  # the redundant API call was avoided


def test_trailing_whitespace_still_hits_cache(client, fake_gemini):
    fake = fake_gemini()
    client.post("/review", json={"language": "Python", "code": "print(1)"})
    r = client.post("/review", json={"language": "Python", "code": "print(1)\n\n"})
    assert r.json()["cached"] is True
    assert fake.calls == 1


def test_different_code_or_language_is_a_cache_miss(client, fake_gemini):
    fake = fake_gemini()
    client.post("/review", json={"language": "Python", "code": "print(1)"})
    client.post("/review", json={"language": "Python", "code": "print(2)"})
    client.post("/review", json={"language": "Java", "code": "print(1)"})
    assert fake.calls == 3


def test_failed_reviews_are_not_cached(client, fake_gemini, valid_payload):
    fake = fake_gemini([api_error(400), json.dumps(GOOD_REVIEW)])
    assert client.post("/review", json=valid_payload).status_code == 502
    second = client.post("/review", json=valid_payload)
    assert second.status_code == 200
    assert second.json()["cached"] is False
    assert fake.calls == 2


def test_rate_limit_returns_429_after_limit(client, fake_gemini, valid_payload):
    fake_gemini()
    # Test config sets the limit to 3/minute
    codes = [client.post("/review", json={**valid_payload, "code": f"x={i}"}).status_code for i in range(4)]
    assert codes == [200, 200, 200, 429]


def test_rate_limit_response_has_retry_after(client, fake_gemini, valid_payload):
    fake_gemini()
    for i in range(3):
        client.post("/review", json={**valid_payload, "code": f"x={i}"})
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 429
    assert r.headers["retry-after"] == "60"


def test_rate_limit_does_not_apply_to_health(client):
    assert all(client.get("/health").status_code == 200 for _ in range(10))
