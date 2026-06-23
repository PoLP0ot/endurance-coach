"""Structured logging tests (3.3)."""
from __future__ import annotations

import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_emits_single_json_line_with_extras():
    record = logging.makeLogRecord(
        {
            "name": "app.request",
            "levelno": logging.INFO,
            "levelname": "INFO",
            "msg": "request",
            "request_id": "abc123",
            "status": 200,
            "duration_ms": 4.2,
        }
    )
    out = JsonFormatter().format(record)
    parsed = json.loads(out)
    assert parsed["logger"] == "app.request"
    assert parsed["level"] == "INFO"
    assert parsed["msg"] == "request"
    assert parsed["request_id"] == "abc123"
    assert parsed["status"] == 200
    assert "ts" in parsed


def test_json_formatter_includes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            "x", logging.ERROR, __file__, 1, "failed", None, exc_info=True
        )
        import sys

        record.exc_info = sys.exc_info()
        parsed = json.loads(JsonFormatter().format(record))
        assert "boom" in parsed["exc"]


def test_request_middleware_sets_request_id_header(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID")
