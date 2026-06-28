"""Middleware de seguridad: security headers, request-id y rate limiting básico."""
from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.infrastructure.cache.redis_client import CacheService

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(self), microphone=(), camera=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()
        response: Response = await call_next(request)
        for key, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(key, value)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{(time.perf_counter() - start) * 1000:.1f}ms"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting distribuido por IP usando Redis (capa de aplicación, además
    del limit en Nginx). Aplica un límite global por ventana de 60s.
    """

    def __init__(self, app, *, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # No limita health checks ni preflight CORS.
        if request.method == "OPTIONS" or request.url.path.startswith(("/health", "/api/health")):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        fwd = request.headers.get("x-forwarded-for")
        if fwd:
            client_ip = fwd.split(",")[0].strip()

        cache = CacheService()
        key = f"ratelimit:{client_ip}:{int(time.time()) // self.window_seconds}"
        try:
            count = await cache.incr_with_ttl(key, self.window_seconds)
        except Exception:  # noqa: BLE001 - si Redis falla, no bloquea tráfico
            return await call_next(request)

        if count > self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"error_code": "rate_limited", "message": "Demasiadas solicitudes."},
                headers={"Retry-After": str(self.window_seconds)},
            )
        return await call_next(request)
