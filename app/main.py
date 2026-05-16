import logging
import time
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import engine
from app.routers import admin_panel, auth, health, participants, van_requests

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


# ── lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("DB connectivity check failed at startup: %s", exc)
    yield
    await engine.dispose()


# ── app ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="MCCTV LFR Vans API", lifespan=lifespan, docs_url="/api/docs")


# ── CORS ──────────────────────────────────────────────────────────────────────

_origins = list({
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── request logging middleware ────────────────────────────────────────────────

class _RequestLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


app.add_middleware(_RequestLogger)


# ── exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    messages = {
        status.HTTP_401_UNAUTHORIZED: "Authentication required",
        status.HTTP_403_FORBIDDEN: "Permission denied",
        status.HTTP_404_NOT_FOUND: "Not found",
    }
    detail = messages.get(exc.status_code, exc.detail)
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        loc = err.get("loc", ())
        # Drop the top-level "body"/"query"/"path" prefix that FastAPI adds
        field_parts = [str(p) for p in loc if p not in ("body", "query", "path")]
        field = ".".join(field_parts) if field_parts else (str(loc[-1]) if loc else "unknown")
        errors.append({"field": field, "message": err["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s %s:\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ── routers ───────────────────────────────────────────────────────────────────

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(van_requests.router, prefix="/api")
app.include_router(participants.router, prefix="/api")
app.include_router(admin_panel.router, prefix="/api")
