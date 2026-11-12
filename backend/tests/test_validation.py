import pytest

from schemas import MAX_CODE_CHARS


@pytest.mark.parametrize(
    "payload",
    [
        {"language": "Python", "code": ""},  # empty
        {"language": "Python", "code": "   \n\t "},  # whitespace only
        {"language": "Python", "code": "x" * (MAX_CODE_CHARS + 1)},  # too long
        {"language": "Ruby", "code": "puts 1"},  # unsupported language
        {"language": "python", "code": "print(1)"},  # wrong case
        {"language": "Python"},  # missing code
        {"code": "print(1)"},  # missing language
        {},  # empty body
        {"language": "Python", "code": 123},  # wrong type
        {"language": ["Python"], "code": "x"},  # wrong type
    ],
)
def test_invalid_payloads_return_422_and_never_call_gemini(client, fake_gemini, payload):
    fake = fake_gemini()
    r = client.post("/review", json=payload)
    assert r.status_code == 422
    assert fake.calls == 0


def test_code_at_max_length_is_accepted(client, fake_gemini):
    fake_gemini()
    r = client.post("/review", json={"language": "C", "code": "x" * MAX_CODE_CHARS})
    assert r.status_code == 200


def test_non_json_body_returns_422(client):
    r = client.post("/review", content="not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_wrong_method_returns_405(client):
    assert client.get("/review").status_code == 405
