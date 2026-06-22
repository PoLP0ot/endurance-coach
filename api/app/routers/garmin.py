"""Garmin connection + import endpoints (US1)."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.core.security import encrypt
from app.jobs.queue import enqueue_garmin_import
from app.models.garmin import GarminConnection
from app.models.import_job import JOB_QUEUED, ImportJob
from app.models.user import User
from app.services.garmin import (
    GarminAccountLocked,
    GarminAuthError,
    GarminConnectProvider,
    GarminMFARequired,
    GarminProvider,
)
from app.services.garmin_import import resolve_since

router = APIRouter(prefix="/garmin", tags=["garmin"])

Enqueuer = Callable[[str, str, str], Awaitable[None]]


def get_garmin_provider() -> GarminProvider:
    """Provider dependency (overridden in tests)."""
    return GarminConnectProvider()


def get_enqueuer() -> Enqueuer:
    """Import-job enqueuer dependency (overridden in tests)."""
    return enqueue_garmin_import


class ConnectRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


def _get_or_create_user(db: Session, current: CurrentUser) -> User:
    user = db.get(User, current.id)
    if user is None:
        user = User(id=current.id, email=current.email)
        db.add(user)
        db.commit()
    return user


def _upsert_connection(
    db: Session, user_id: str, encrypted: str, username: str
) -> GarminConnection:
    conn = (
        db.query(GarminConnection).filter_by(user_id=user_id).one_or_none()
    )
    if conn is None:
        conn = GarminConnection(
            user_id=user_id,
            encrypted_tokens=encrypted,
            garmin_username=username,
            status="connected",
        )
        db.add(conn)
    else:
        conn.encrypted_tokens = encrypted
        conn.garmin_username = username
        conn.status = "connected"
    db.commit()
    db.refresh(conn)
    return conn


def _queue_import(db: Session, user_id: str) -> ImportJob:
    job = ImportJob(user_id=user_id, status=JOB_QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/connect", status_code=status.HTTP_202_ACCEPTED)
async def connect(
    body: ConnectRequest,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    provider: GarminProvider = Depends(get_garmin_provider),
    enqueue: Enqueuer = Depends(get_enqueuer),
) -> dict:
    """Authenticate with Garmin, store the encrypted token, enqueue an import."""
    try:
        token = provider.login(body.username, body.password)
    except GarminMFARequired as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "garmin_mfa_required") from exc
    except GarminAccountLocked as exc:
        raise HTTPException(status.HTTP_423_LOCKED, "garmin_account_locked") from exc
    except GarminAuthError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "garmin_auth_failed"
        ) from exc

    _get_or_create_user(db, user)
    conn = _upsert_connection(db, user.id, encrypt(token), body.username)
    since = resolve_since(conn, date.today())
    job = _queue_import(db, user.id)
    await enqueue(user.id, job.id, since.isoformat())
    return {"job_id": job.id, "status": job.status}


@router.get("/status")
async def garmin_status(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Report whether the user has a connected Garmin account."""
    conn = db.query(GarminConnection).filter_by(user_id=user.id).one_or_none()
    if conn is None:
        return {"status": "disconnected", "last_sync_at": None}
    return {
        "status": conn.status,
        "garmin_username": conn.garmin_username,
        "last_sync_at": conn.last_sync_at.isoformat() if conn.last_sync_at else None,
    }


@router.get("/import-status/{job_id}")
async def import_status(
    job_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Poll import progress. Enforces ownership of the job (SEC4)."""
    job = db.get(ImportJob, job_id)
    if job is None or job.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "job_not_found")
    return {
        "job_id": job.id,
        "status": job.status,
        "progress_label": job.progress_label,
        "activities_imported": job.activities_imported,
        "health_days_imported": job.health_days_imported,
        "error": job.error,
    }


@router.post("/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    enqueue: Enqueuer = Depends(get_enqueuer),
) -> dict:
    """Incremental re-import of activities since the last sync (ST3.3)."""
    conn = db.query(GarminConnection).filter_by(user_id=user.id).one_or_none()
    if conn is None or conn.status != "connected":
        raise HTTPException(status.HTTP_409_CONFLICT, "garmin_not_connected")
    since = resolve_since(conn, date.today())
    job = _queue_import(db, user.id)
    await enqueue(user.id, job.id, since.isoformat())
    return {"job_id": job.id, "status": job.status, "since": since.isoformat()}


@router.post("/disconnect")
async def disconnect(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Disconnect Garmin but keep imported data (ST3.6)."""
    conn = db.query(GarminConnection).filter_by(user_id=user.id).one_or_none()
    if conn is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "garmin_not_connected")
    conn.status = "disconnected"
    db.add(conn)
    db.commit()
    return {"status": "disconnected"}
