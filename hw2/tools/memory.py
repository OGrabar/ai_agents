import json
import time
from pathlib import Path

JOURNAL, FACTS_FILE = Path("episodes.jsonl"), Path("facts.json")
_index = _search = _embed = _has_collection = None


def configure(index, search, embed, has_collection):
    """index(name, chunks, vectors), search(name, query, k) -> hits with text, embed(texts) -> vectors, has_collection(name) -> bool"""
    global _index, _search, _embed, _has_collection
    _index, _search, _embed, _has_collection = index, search, embed, has_collection


def known_facts():
    return json.loads(FACTS_FILE.read_text(encoding="utf-8")) if FACTS_FILE.exists() else []


def store_facts(facts):
    FACTS_FILE.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    if facts:
        _index("facts", [{"page": "memory", "section": "", "url": "", "text": f} for f in facts], _embed(facts))


def remember_episode(session, role, text):
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"session": session, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "role": role, "text": text}, ensure_ascii=False) + "\n")


def recall_facts(question, k=3):
    if not _has_collection("facts"):
        return []
    return [h["text"] for h in _search("facts", question, k)]
