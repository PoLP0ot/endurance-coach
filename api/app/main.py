"""FastAPI application entrypoint.

Wires CORS, a consistent error envelope, and routers.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.routers import (
    activities,
    chat,
    dashboard,
    email,
    garmin,
    health,
    plans,
    subscriptions,
)


def create_app() -> FastAPI:
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

    # --- Consistent error envelope: {"error": {"code", "message", "details"}} ---
    @app.exception_handler(StarletteHTTPException)
    async def http_exc_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.status_code, "message": exc.detail}},
            headers=getattr(exc, "headers", None),
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
    app.include_router(activities.router)
    app.include_router(chat.router)
    app.include_router(plans.router)
    app.include_router(subscriptions.router)
    app.include_router(email.router)
    return app


app = create_app()
