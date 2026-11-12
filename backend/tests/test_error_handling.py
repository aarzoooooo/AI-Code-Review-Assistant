import json

import gemini_service
from tests.conftest import GOOD_REVIEW, api_error


def test_transient_error_is_retried_then_succeeds(client, fake_gemini, valid_payload):
    fake = fake_gemini([api_error(503), json.dumps(GOOD_REVIEW)])
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 200
    assert fake.calls == 2


def test_rate_limited_by_gemini_exhausts_retries_returns_503(client, fake_gemini, valid_payload):
    fake = fake_gemini([api_error(429), api_error(429)])
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 503
    assert "busy" in r.json()["detail"].lower()
    assert fake.calls == 2


def test_non_retryable_error_returns_502_without_retry(client, fake_gemini, valid_payload):
    fake = fake_gemini([api_error(400)])
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 502
    assert fake.calls == 1


def test_upstream_error_details_are_not_leaked(client, fake_gemini, valid_payload):
    fake_gemini([api_error(403)])
    r = client.post("/review", json=valid_payload)
    assert "fake 403" not in r.text


def test_empty_model_response_returns_502(client, fake_gemini, valid_payload):
    fake_gemini([""])
    assert client.post("/review", json=valid_payload).status_code == 502


def test_invalid_json_from_model_returns_502(client, fake_gemini, valid_payload):
    fake_gemini(["this is not json"])
    assert client.post("/review", json=valid_payload).status_code == 502


def test_json_with_wrong_shape_returns_502(client, fake_gemini, valid_payload):
    fake_gemini([json.dumps({"unexpected": True})])
    assert client.post("/review", json=valid_payload).status_code == 502


def test_unexpected_exception_returns_502_json(client, fake_gemini, valid_payload):
    fake_gemini([ConnectionError("network down")])
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 502
    assert "detail" in r.json()


def test_missing_api_key_returns_503(client, monkeypatch, valid_payload):
    monkeypatch.setattr(gemini_service, "_client", None)
    monkeypatch.setattr(gemini_service.config, "GEMINI_API_KEY", None)
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 503


def test_falls_back_to_next_model(client, fake_gemini, monkeypatch, valid_payload):
    monkeypatch.setattr(gemini_service.config, "GEMINI_MODELS", ["model-a", "model-b"])
    fake = fake_gemini(["", json.dumps(GOOD_REVIEW)])  # model-a empty -> model-b works
    r = client.post("/review", json=valid_payload)
    assert r.status_code == 200
    assert fake.calls == 2
