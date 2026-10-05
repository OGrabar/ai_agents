import re

from pydantic import BaseModel, Field

from .http import http_request, tool_errors

WIKI = "https://en.wikipedia.org/w/api.php"
WIKI_HEADERS = {"User-Agent": "agents-course-seminar01/1.0 (https://postypashki.ru; educational project)"}


class WikiSearchArgs(BaseModel):
    query: str = Field(description="short search query: a name, a title, a term")


class WikiPageFindArgs(BaseModel):
    title: str = Field(description='exact article title, for example "2025 in Japan" or "Progress MS-33"')
    keywords: str = Field(description="two to five keywords from the question")


def wiki(params, attempts=3):
    r = http_request("GET", WIKI, "Wikipedia", attempts=attempts,
                     headers=WIKI_HEADERS, params={**params, "format": "json"})
    if not r.headers.get("content-type", "").startswith("application/json"):
        raise RuntimeError("Wikipedia error: unexpected content type")
    return r.json()["query"]


@tool_errors
def wiki_search(query: str) -> str:
    hits = wiki({"action": "query", "list": "search", "srsearch": query, "srlimit": 1})["search"]

    if not hits:
        return "No data"
    pages = wiki({"action":"query", "prop": "extracts", "explaintext": 1, "exintro": 1, "titles": hits[0]["title"]})["pages"]
    text = " ".join(next(iter(pages.values())).get("extract", "").split())
    return f"[{hits[0]["title"]}] {text[:5000]}"


@tool_errors
def wiki_page_find(title: str, keywords: str) -> str:
    pages = wiki({"action": "query", "prop": "extracts", "explaintext": 1, "titles": title, "redirects": 1})["pages"]
    page = next(iter(pages.values()))
    text = page.get("extract", "")
    if not text:
        return "No such page"
    words = [w for w in re.findall(r"\w+", keywords.lower()) if len(w) > 2]
    if not words:
        return "No keywords given"
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    hits = [line for line in lines if sum(w in line.lower() for w in words) >= max(1, (len(words) + 1) // 2)]
    if not hits:
        return "Keywords not found on the page"
    return "\n".join([f"[{page.get('title', title)}]"] + [line[:350] for line in hits[:5]])
