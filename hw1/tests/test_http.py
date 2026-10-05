import pytest

from fakes import FakeResponse, fake_request
from tools import http


def test_http_request_ok(monkeypatch):
    monkeypatch.setattr(http.requests, "request", fake_request([FakeResponse(data={"ok": True})]))
    assert http.http_request("GET", "https://example.org", "Example").json() == {"ok": True}


def test_http_request_retries_and_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr(http.time, "sleep", sleeps.append)
    calls = []
    responses = [FakeResponse(status_code=500, text="boom"), FakeResponse(data={"ok": True})]
    monkeypatch.setattr(http.requests, "request", fake_request(responses, calls))
    assert http.http_request("GET", "https://example.org", "Example").json() == {"ok": True}
    assert len(calls) == 2
    assert sleeps == [http.backoff(0)]


def test_http_request_fails_fast_on_4xx(monkeypatch):
    sleeps = []
    monkeypatch.setattr(http.time, "sleep", sleeps.append)
    calls = []
    monkeypatch.setattr(http.requests, "request", fake_request([FakeResponse(status_code=404, text="nope")], calls))
    with pytest.raises(RuntimeError, match="Example error: HTTP 404"):
        http.http_request("GET", "https://example.org", "Example")
    assert len(calls) == 1
    assert sleeps == []


def test_http_request_gives_up_after_attempts(monkeypatch):
    monkeypatch.setattr(http.time, "sleep", lambda seconds: None)
    calls = []
    responses = [FakeResponse(status_code=503, text="down")] * 3
    monkeypatch.setattr(http.requests, "request", fake_request(responses, calls))
    with pytest.raises(RuntimeError, match="Example error: HTTP 503"):
        http.http_request("GET", "https://example.org", "Example")
    assert len(calls) == 3
