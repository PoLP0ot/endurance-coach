"""Structured logging setup.

Emits one JSON object per log record in non-development environments (easy to
ship to a log aggregator) and a readable line locally. Any extra fields passed
via ``logger.info(msg, extra={...})`` are merged into the record.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

# Fields the LogRecord always carries; everything else is treated as structured
# context added by the caller via ``extra=``.
_RESERVED = set(
    logging.makeLogRecord({}).__dict__
) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    """Render a log record (plus any ``extra`` fields) as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO", *, json_logs: bool = True) -> None:
    """Configure the root logger once. Idempotent across calls."""
    root = logging.getLogger()
    root.setLevel(level.upper())
    handler = logging.StreamHandler()
    if json_logs:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s · %(message)s")
        )
    root.handlers = [handler]
