import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.proxy import forward_request

settings = get_settings()
logger = structlog.get_logger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests}/minute"],
)

app = FastAPI(
    title="LMS API Gateway",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def gateway_proxy(request: Request, path: str):
    """Catch-all proxy — forwards /api/* to the backend."""
    try:
        return await forward_request(request)
    except Exception as exc:
        logger.error("gateway_proxy_error", path=path, error=str(exc))
        return JSONResponse(
            status_code=502,
            content={"success": False, "message": "Gateway error"},
        )
