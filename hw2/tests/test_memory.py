import json

import pytest

from tools import memory


class FakeStore:
    """Stands in for Milvus and the embedder: index replaces a collection, search ranks by shared words."""

    def __init__(self):
        self.collections = {}

    def index(self, name, chunks, vectors):
        assert len(chunks) == len(vectors)
        self.collections[name] = [c["text"] for c in chunks]

    def search(self, name, query, k):
        words = set(query.lower().split())
        ranked = sorted(self.collections[name], key=lambda t: -len(words & set(t.lower().split())))
        return [{"text": t} for t in ranked[:k]]

    def embed(self, texts):
        return [[float(len(t))] for t in texts]

    def has_collection(self, name):
        return name in self.collections


@pytest.fixture
def store(monkeypatch, tmp_path):
    monkeypatch.setattr(memory, "JOURNAL", tmp_path / "episodes.jsonl")
    monkeypatch.setattr(memory, "FACTS_FILE", tmp_path / "facts.json")
    fake = FakeStore()
    memory.configure(fake.index, fake.search, fake.embed, fake.has_collection)
    return fake


def test_empty_memory(store):
    assert memory.known_facts() == []
    assert memory.recall_facts("where do I live") == []
    assert not memory.JOURNAL.exists()


def test_stored_fact_is_found(store):
    memory.store_facts(["Lives in Novosibirsk", "Follows space and hockey"])
    assert memory.known_facts() == ["Lives in Novosibirsk", "Follows space and hockey"]
    assert memory.recall_facts("hockey news", k=1) == ["Follows space and hockey"]


def test_new_fact_replaces_old_one(store):
    memory.store_facts(["Lives in Novosibirsk", "Follows hockey"])
    memory.store_facts(["Lives in Kaliningrad", "Follows football"])
    assert memory.known_facts() == ["Lives in Kaliningrad", "Follows football"]
    assert store.collections["facts"] == ["Lives in Kaliningrad", "Follows football"]
    found = memory.recall_facts("Novosibirsk hockey", k=5)
    assert "Lives in Novosibirsk" not in found and "Follows hockey" not in found


def test_episodes_go_to_journal_not_to_facts(store):
    memory.remember_episode("s1", "user", "Привет, я Лена")
    memory.remember_episode("s1", "assistant", "Привет!")
    rows = [json.loads(line) for line in memory.JOURNAL.read_text(encoding="utf-8").splitlines()]
    assert [(r["session"], r["role"], r["text"]) for r in rows] == [("s1", "user", "Привет, я Лена"), ("s1", "assistant", "Привет!")]
    assert all(r["time"] for r in rows)
    assert memory.known_facts() == [] and memory.recall_facts("Лена") == []
