from pydantic import BaseModel, Field

from .errors import tool_errors

TOP_K = 5
_search = None


class KBArgs(BaseModel):
    query: str = Field(description="short search query in English: names, dates, key terms of the event")
    page: str = Field(default="", description="optional exact page title to search within, for example '2026 in Japan'; empty means all pages")


def configure(search):
    """search(query, k, flt) -> list of hits with page, section, text"""
    global _search
    _search = search


def search_chunks(query, k, flt):
    if _search is None:
        raise RuntimeError("knowledge base is not configured")
    return _search(query, k, flt)


@tool_errors
def knowledge_base(query: str, page: str = "") -> str:
    if not query.strip():
        return "No query given"
    flt = 'page == "{}"'.format(page.replace('"', '\\"')) if page else ""
    hits = search_chunks(query, TOP_K, flt)
    if not hits:
        return "nothing found"
    return "\n".join(f"[{h['page']} / {h['section']}] {h['text']}" for h in hits)
