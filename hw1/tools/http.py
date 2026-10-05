import time
from functools import wraps

import requests

RETRYABLE = (429, 500, 502, 503, 504)


def backoff(attempt):
    return min(30, 1.5 * 2 ** attempt)


def tool_errors(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return f"tool error: {e}"
    return wrapper


def http_request(method, url, source, attempts=3, timeout=15, **kwargs):
    problem = "no response"
    for attempt in range(attempts):
        try:
            r = requests.request(method, url, timeout=timeout, **kwargs)
        except requests.RequestException as e:
            problem = type(e).__name__
        else:
            if r.status_code == 200:
                return r
            problem = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code not in RETRYABLE:
                break
        time.sleep(backoff(attempt))
    raise RuntimeError(f"{source} error: {problem}")
