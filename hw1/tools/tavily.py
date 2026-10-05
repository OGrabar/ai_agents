import os

from pydantic import BaseModel, Field

from .http import http_request, tool_errors

TAVILY_URL = "https://api.tavily.com/search"


class TavilyArgs(BaseModel):
    query: str = Field(description="short web search query: a name, a title, a term")


@tool_errors
def tavily_search(query: str) -> str:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return "TAVILY_API_KEY is not set"
    r = http_request("POST", TAVILY_URL, "Tavily", timeout=20,
                     headers={"Authorization": f"Bearer {key}"},
                     json={"query": query, "max_results": 3, "search_depth": "basic"})
    results = (r.json() or {}).get("results") or []
    if not results:
        return "No data"
    return "\n".join(f"[{x.get('title', '')}] {x.get('url', '')} "
                     f"{' '.join(str(x.get('content', '')).split())[:1500]}"
                     for x in results[:3])
