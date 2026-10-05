import pytest

from fakes import fake_wiki
from tools import wiki


def test_wiki_search_normal(monkeypatch):
    calls = []
    monkeypatch.setattr(wiki, "wiki", fake_wiki([{"title": "Ed Wood"}], "Edward Wood was a\nfilmmaker.", calls))
    result = wiki.wiki_search("Ed Wood film")
    assert result == "[Ed Wood] Edward Wood was a filmmaker."
    assert calls[0] == {"action": "query", "list": "search", "srsearch": "Ed Wood film", "srlimit": 1}
    assert calls[1]["titles"] == "Ed Wood"
    assert calls[1]["prop"] == "extracts"
    assert calls[1]["exintro"] == 1
    assert calls[1]["explaintext"] == 1


def test_wiki_search_empty(monkeypatch):
    monkeypatch.setattr(wiki, "wiki", fake_wiki(calls=[]))
    assert wiki.wiki_search("Ed Wood") == "No data"


def test_wiki_search_error(monkeypatch):
    def broken(params):
        raise RuntimeError("Wikipedia error: test failure")
    monkeypatch.setattr(wiki, "wiki", broken)
    assert wiki.wiki_search("Ed Wood") == "tool error: Wikipedia error: test failure"


def test_wiki_page_find_normal(monkeypatch):
    page = ("Intro line.\n== March ==\n"
            "10 March - Heavy rain floods the capital.\n"
            "15 March - Ukraine boycotts the closing ceremony of the Paralympics.\n")
    calls = []
    monkeypatch.setattr(wiki, "wiki", fake_wiki(extract=page, calls=calls))
    result = wiki.wiki_page_find("2026 in Ukraine", "Ukraine boycott ceremony")
    assert result == ("[2026 in Ukraine]\n"
                      "15 March - Ukraine boycotts the closing ceremony of the Paralympics.")
    assert "Heavy rain" not in result
    assert calls[0]["titles"] == "2026 in Ukraine"
    assert calls[0]["prop"] == "extracts"
    assert "exintro" not in calls[0]
    assert calls[0]["redirects"] == 1


def test_wiki_page_find_truncates_long_lines(monkeypatch):
    long_line = "15 March - " + "word " * 100
    monkeypatch.setattr(wiki, "wiki", fake_wiki(extract=long_line))
    lines = wiki.wiki_page_find("Long", "word").splitlines()
    assert lines[0] == "[Long]"
    assert len(lines[1]) == 350


def test_wiki_page_find_limits_hits(monkeypatch):
    page = "\n".join(f"{i} March - flood event number {i}" for i in range(1, 10))
    monkeypatch.setattr(wiki, "wiki", fake_wiki(extract=page))
    lines = wiki.wiki_page_find("Floods", "flood").splitlines()
    assert len(lines) == 6


def test_wiki_page_find_no_such_page(monkeypatch):
    monkeypatch.setattr(wiki, "wiki", fake_wiki(extract=""))
    assert wiki.wiki_page_find("Missing", "word") == "No such page"


def test_wiki_page_find_no_keywords(monkeypatch):
    monkeypatch.setattr(wiki, "wiki", fake_wiki(extract="some text here"))
    assert wiki.wiki_page_find("Page", "a b c") == "No keywords given"


def test_wiki_page_find_keywords_not_found(monkeypatch):
    monkeypatch.setattr(wiki, "wiki", fake_wiki(extract="one\ntwo lines\n"))
    assert wiki.wiki_page_find("Page", "absent") == "Keywords not found on the page"


def test_wiki_page_find_error(monkeypatch):
    def broken(params):
        raise RuntimeError("Wikipedia error: test failure")
    monkeypatch.setattr(wiki, "wiki", broken)
    assert wiki.wiki_page_find("Page", "word") == "tool error: Wikipedia error: test failure"


@pytest.mark.network
def test_wiki_search_live():
    result = wiki.wiki_search("Scott Derrickson")
    assert result.startswith("[Scott Derrickson]")
    assert "Derrickson" in result[len("[Scott Derrickson]"):]
    assert len(result) > 100


@pytest.mark.network
def test_wiki_page_find_live():
    result = wiki.wiki_page_find("2026 FIFA World Cup", "FIFA, soccer, football, group")
    assert result.startswith("[2026 FIFA World Cup]")
    assert "FIFA World Cup" in result
    assert len(result) > 100


@pytest.mark.network
def test_wiki_page_find_live_ukraine():
    result = wiki.wiki_page_find("2026 in Ukraine", "Ukraine boycott ceremony")
    assert result.startswith("[2026 in Ukraine]")
    assert "boycott" in result.lower()


