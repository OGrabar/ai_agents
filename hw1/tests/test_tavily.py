import pytest

from fakes import FakeResponse, fake_http
from tools import tavily


def test_tavily_search_normal(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = []
    response = FakeResponse(data={"results": [
        {"title": "Ed Wood", "url": "https://example.org/ed", "content": "Edward\nWood  was a filmmaker."},
        {"title": "Ed Wood (film)", "url": "https://example.org/film", "content": "A 1955 film."},
    ]})
    monkeypatch.setattr(tavily, "http_request", fake_http(response, calls))
    result = tavily.tavily_search("Ed Wood")
    assert result == ("[Ed Wood] https://example.org/ed Edward Wood was a filmmaker.\n"
                      "[Ed Wood (film)] https://example.org/film A 1955 film.")
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == tavily.TAVILY_URL
    assert calls[0]["source"] == "Tavily"
    assert calls[0]["headers"] == {"Authorization": "Bearer test-key"}
    assert calls[0]["json"]["query"] == "Ed Wood"


def test_tavily_search_empty(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    monkeypatch.setattr(tavily, "http_request", fake_http(FakeResponse(data={"results": []})))
    assert tavily.tavily_search("Ed Wood") == "No data"


def test_tavily_search_error(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = []

    def broken(*args, **kwargs):
        calls.append((args, kwargs))
        raise RuntimeError("Tavily error: HTTP 404: not found")
    monkeypatch.setattr(tavily, "http_request", broken)
    assert tavily.tavily_search("Ed Wood") == "tool error: Tavily error: HTTP 404: not found"
    assert len(calls) == 1


def test_tavily_search_without_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("network call without a key")
    monkeypatch.setattr(tavily, "http_request", forbidden)
    assert tavily.tavily_search("Ed Wood") == "TAVILY_API_KEY is not set"


@pytest.mark.network
def test_tavily_search_live():
    if not tavily.os.getenv("TAVILY_API_KEY"):
        pytest.skip("TAVILY_API_KEY is not set")
    result = tavily.tavily_search("Scott Derrickson")
    assert result and not result.startswith("tool error")
    assert result.startswith("[")
