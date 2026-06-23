"""Enqueue helper tests — Redis-less inline import fallback (0.1/3.1)."""
from __future__ import annotations

import pytest
from app.jobs import queue


@pytest.mark.asyncio
async def test_enqueue_falls_back_to_inline_when_redis_down(monkeypatch):
    """With no Redis, the import runs inline so the dev flow still completes."""
    calls: list[tuple] = []

    async def _boom(*_args, **_kwargs):
        raise ConnectionError("redis unreachable")

    async def _inline(ctx, user_id, job_id, since_iso):
        calls.append((user_id, job_id, since_iso))
        return {"imported": 0}

    monkeypatch.setattr(queue, "create_pool", _boom, raising=False)
    monkeypatch.setattr("arq.create_pool", _boom)
    monkeypatch.setattr(
        "app.jobs.worker.import_garmin_activities", _inline
    )

    await queue.enqueue_garmin_import("u1", "j1", "2026-06-01")
    assert calls == [("u1", "j1", "2026-06-01")]


@pytest.mark.asyncio
async def test_enqueue_uses_pool_when_redis_available(monkeypatch):
    """When Redis is reachable the job is enqueued, not run inline."""
    enqueued: list[tuple] = []

    class _Pool:
        async def enqueue_job(self, name, *args):
            enqueued.append((name, *args))

        async def close(self):
            return None

    async def _pool(*_args, **_kwargs):
        return _Pool()

    monkeypatch.setattr("arq.create_pool", _pool)

    async def _fail_inline(*_a, **_k):
        raise AssertionError("inline import should not run when Redis is up")

    monkeypatch.setattr("app.jobs.worker.import_garmin_activities", _fail_inline)

    await queue.enqueue_garmin_import("u2", "j2", "2026-06-02")
    assert enqueued == [("import_garmin_activities", "u2", "j2", "2026-06-02")]
