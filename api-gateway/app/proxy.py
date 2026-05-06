"""
Reverse-proxy logic: forward requests to the backend and stream responses back.
"""
import httpx
from fastapi import Request, Response

from app.config import get_settings

settings = get_settings()

# Shared async client — reused across requests
_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=settings.backend_url,
            timeout=httpx.Timeout(30.0),
            follow_redirects=False,
        )
    return _client


# Headers that must not be forwarded upstream
HOP_BY_HOP = frozenset(
    [
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
    ]
)


async def forward_request(request: Request) -> Response:
    client = get_http_client()

    # Build upstream headers
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in HOP_BY_HOP
    }
    headers["X-Forwarded-For"] = request.client.host if request.client else "unknown"
    headers["X-Forwarded-Proto"] = request.url.scheme

    body = await request.body()

    upstream_response = await client.request(
        method=request.method,
        url=request.url.path,
        params=request.query_params,
        headers=headers,
        content=body,
        cookies=dict(request.cookies),
    )

    # Strip hop-by-hop from response
    response_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower() not in HOP_BY_HOP
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
