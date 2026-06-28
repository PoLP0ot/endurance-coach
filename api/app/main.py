"""FastAPI application entrypoint.

Wires CORS, a consistent error envelope, and routers.
"""
from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import configure_logging
from app.routers import (
    activities,
    chat,
    coach,
    dashboard,
    email,
    garmin,
    gdpr,
    health,
    plans,
    signals,
    subscriptions,
    users,
)
from app.services.llm import LLMError


def create_app() -> FastAPI:
    configure_logging(
        settings.log_level, json_logs=settings.environment != "development"
    )
    request_logger = logging.getLogger("app.request")

    app = FastAPI(
        title="Endurance Coach API",
        version="0.1.0",
        description="AI coaching platform for endurance athletes.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Emit one structured line per request with a correlation id + latency."""
        request_id = uuid.uuid4().hex[:12]
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            request_logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": elapsed_ms,
                },
            )
            raise
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        request_logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": elapsed_ms,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response

    # --- Consistent error envelope: {"error": {"code", "message", "details"}} ---
    @app.exception_handler(StarletteHTTPException)
    async def http_exc_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.status_code, "message": exc.detail}},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(LLMError)
    async def llm_exc_handler(request: Request, exc: LLMError):
        # 503 when a retry could plausibly succeed (timeout / throttle / provider
        # blip), 502 for terminal failures (quota exhausted, auth, misconfig).
        code = 503 if exc.retryable else 502
        return JSONResponse(
            status_code=code,
            content={
                "error": {
                    "code": code,
                    "message": "coach_unavailable",
                    "reason": exc.reason,
                    "retryable": exc.retryable,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exc_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": exc.errors(),
                }
            },
        )

    app.include_router(health.router)
    app.include_router(garmin.router)
    app.include_router(dashboard.router)
    app.include_router(signals.router)
    app.include_router(coach.router)
    app.include_router(activities.router)
    app.include_router(chat.router)
    app.include_router(plans.router)
    app.include_router(subscriptions.router)
    app.include_router(email.router)
    app.include_router(users.router)
    app.include_router(gdpr.router)
    return app


app = create_app()
