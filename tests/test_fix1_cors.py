import pytest
from govisense.config import settings
from govisense.api.main import app


def test_cors_origins_configured():
    assert hasattr(settings, "cors_origins")
    assert isinstance(settings.cors_origins, list)
    assert len(settings.cors_origins) > 0
    assert "http://localhost:5173" in settings.cors_origins


@pytest.mark.anyio
async def test_cors_allowed_and_disallowed_origins():
    # Test allowed origin via ASGI receive/send
    allowed_origin = "http://localhost:5173"
    disallowed_origin = "http://malicious-attacker.com"

    # Preflight OPTIONS request for allowed origin
    scope_allowed = {
        "type": "http",
        "method": "OPTIONS",
        "path": "/health",
        "raw_path": b"/health",
        "query_string": b"",
        "headers": [
            (b"origin", allowed_origin.encode()),
            (b"access-control-request-method", b"GET"),
        ],
    }
    response_headers_allowed = []

    async def send_allowed(message):
        if message["type"] == "http.response.start":
            response_headers_allowed.extend(message.get("headers", []))

    async def receive():
        return {"type": "http.request"}

    await app(scope_allowed, receive, send_allowed)
    header_dict_allowed = {k.decode().lower(): v.decode() for k, v in response_headers_allowed}
    assert header_dict_allowed.get("access-control-allow-origin") == allowed_origin

    # Preflight OPTIONS request for disallowed origin
    scope_disallowed = {
        "type": "http",
        "method": "OPTIONS",
        "path": "/health",
        "raw_path": b"/health",
        "query_string": b"",
        "headers": [
            (b"origin", disallowed_origin.encode()),
            (b"access-control-request-method", b"GET"),
        ],
    }
    response_headers_disallowed = []
    status_code_disallowed = []

    async def send_disallowed(message):
        if message["type"] == "http.response.start":
            status_code_disallowed.append(message.get("status"))
            response_headers_disallowed.extend(message.get("headers", []))

    await app(scope_disallowed, receive, send_disallowed)
    header_dict_disallowed = {k.decode().lower(): v.decode() for k, v in response_headers_disallowed}
    # For disallowed origin, CORS middleware either returns 400 or does not include allow-origin header
    assert header_dict_disallowed.get("access-control-allow-origin") is None or status_code_disallowed[0] == 400

