from tools import kb

HITS = [{"page": "2026 in Japan", "section": "April", "text": "April 20 - A magnitude 7.7 earthquake hits off the coast."},
        {"page": "2026 in Japan", "section": "May", "text": "May 15 - A magnitude 6.3 earthquake strikes."}]


def fake_search(hits, calls=None):
    def search(query, k, flt):
        if calls is not None:
            calls.append({"query": query, "k": k, "flt": flt})
        return hits
    return search


def test_knowledge_base_normal(monkeypatch):
    calls = []
    monkeypatch.setattr(kb, "search_chunks", fake_search(HITS, calls))
    result = kb.knowledge_base("earthquake magnitude")
    assert result == ("[2026 in Japan / April] April 20 - A magnitude 7.7 earthquake hits off the coast.\n"
                      "[2026 in Japan / May] May 15 - A magnitude 6.3 earthquake strikes.")
    assert calls == [{"query": "earthquake magnitude", "k": 5, "flt": ""}]


def test_knowledge_base_page_filter(monkeypatch):
    calls = []
    monkeypatch.setattr(kb, "search_chunks", fake_search(HITS, calls))
    kb.knowledge_base("earthquake", page="2026 in Japan")
    assert calls[0]["flt"] == 'page == "2026 in Japan"'


def test_knowledge_base_escapes_quotes_in_page(monkeypatch):
    calls = []
    monkeypatch.setattr(kb, "search_chunks", fake_search(HITS, calls))
    kb.knowledge_base("x", page='Say "hi"')
    assert calls[0]["flt"] == 'page == "Say \\"hi\\""'


def test_knowledge_base_empty(monkeypatch):
    calls = []
    monkeypatch.setattr(kb, "search_chunks", fake_search([], calls))
    assert kb.knowledge_base("Lisbon earthquake") == "nothing found"
    assert kb.knowledge_base("   ") == "No query given"
    assert len(calls) == 1


def test_knowledge_base_error(monkeypatch):
    def broken(query, k, flt):
        raise RuntimeError("Milvus error: test failure")
    monkeypatch.setattr(kb, "search_chunks", broken)
    assert kb.knowledge_base("anything") == "tool error: Milvus error: test failure"


def test_knowledge_base_not_configured(monkeypatch):
    monkeypatch.setattr(kb, "_search", None)
    assert kb.knowledge_base("anything") == "tool error: knowledge base is not configured"


def test_schema_registered():
    kb_args = kb.KBArgs.model_json_schema()
    assert kb_args["required"] == ["query"]
    assert set(kb_args["properties"]) == {"query", "page"}
