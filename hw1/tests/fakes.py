class FakeResponse:
    def __init__(self, status_code=200, data=None, text="", headers=None):
        self.status_code = status_code
        self._data = data if data is not None else {}
        self.text = text
        self.headers = headers if headers is not None else {"content-type": "application/json"}

    def json(self):
        return self._data


def fake_http(response=None, calls=None):
    def fake(method, url, source, **kwargs):
        if calls is not None:
            calls.append({"method": method, "url": url, "source": source, **kwargs})
        return response if response is not None else FakeResponse()
    return fake


def fake_request(responses, calls=None):
    queue = list(responses)

    def fake(method, url, **kwargs):
        if calls is not None:
            calls.append({"method": method, "url": url, **kwargs})
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item
    return fake


def fake_wiki(hits=None, extract=None, calls=None):
    def fake(params):
        if calls is not None:
            calls.append(params)
        if params.get("list") == "search":
            return {"search": hits or []}
        return {"pages": {"1": {"title": params["titles"], "extract": extract}}}
    return fake
