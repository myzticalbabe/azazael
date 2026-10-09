# coding: utf-8
"""CORE/logging.py — StructuredLogger facade (2026-09-11 audit).

tests/test_logging.py specified this module (get_logger caching,
configure_logging, StructuredLogger with dict/kwarg payloads and a JSON
schema of level/source/message/timestamp/thread_id/pid), but only
logging_config.py existed — with a different schema and no wrapper class.
This module implements the tested contract on top of stdlib logging,
creating no global side effects (it never touches the root logger, so
importing it in tests cannot reconfigure production logging).
"""
import io
import json
import logging
import os
import sys
import threading
from datetime import datetime, timezone
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

__all__ = ["StructuredLogger", "get_logger", "configure_logging",
           "JsonFormatterCompat"]

_LEVELS = {
    "debug": logging.DEBUG, "info": logging.INFO,
    "warning": logging.WARNING, "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

_loggers: dict = {}
_default_level = logging.INFO
_cache_lock = threading.Lock()


class _StructuredJsonFormatter(logging.Formatter):
    """JSON schema pinned by tests/test_logging.py."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "source": record.name,
            "message": record.getMessage(),
            "thread_id": record.thread,
            "pid": record.process,
        }
        data = getattr(record, "az_data", None)
        if isinstance(data, dict) and data:
            entry["data"] = data
        return json.dumps(entry, ensure_ascii=False, default=str)


def JsonFormatterCompat(*args, **kwargs):
    """Alias kept for readers of the old name; same schema."""
    return _StructuredJsonFormatter(*args, **kwargs)


class StructuredLogger:
    """Named structured logger. Payloads go under 'data' via extras —
    never as %-args (which is how naive wrappers crash on dicts)."""

    def __init__(self, name: str):
        self.name = name
        # Inner logger carries the exact name: the JSON schema's "source"
        # field is record.name, and the contract pins source == name.
        inner = logging.getLogger(name)
        inner.setLevel(_default_level)
        inner.propagate = False
        if not inner.handlers:
            inner.addHandler(logging.StreamHandler(sys.stderr))
        for h in inner.handlers:
            h.setFormatter(_StructuredJsonFormatter())
        self._logger = inner

    def _emit(self, level: int, message: str, data=None, **kw):
        payload = {}
        if isinstance(data, dict):
            payload.update(data)
        payload.update(kw)
        self._logger.log(level, str(message), extra={"az_data": payload})

    def debug(self, message: str, data=None, **kw):
        self._emit(logging.DEBUG, message, data, **kw)

    def info(self, message: str, data=None, **kw):
        self._emit(logging.INFO, message, data, **kw)

    def warning(self, message: str, data=None, **kw):
        self._emit(logging.WARNING, message, data, **kw)

    def error(self, message: str, data=None, **kw):
        self._emit(logging.ERROR, message, data, **kw)

    def critical(self, message: str, data=None, **kw):
        self._emit(logging.CRITICAL, message, data, **kw)


def get_logger(name: str) -> StructuredLogger:
    """Cached StructuredLogger per name (identity-stable)."""
    with _cache_lock:
        if name not in _loggers:
            _loggers[name] = StructuredLogger(name)
        return _loggers[name]


def configure_logging(level: str = "INFO") -> None:
    """Set the level for all current and future StructuredLoggers."""
    global _default_level
    _default_level = _LEVELS.get(str(level).lower(), logging.INFO)
    with _cache_lock:
        for logger in _loggers.values():
            logger._logger.setLevel(_default_level)


# Re-export the production JSON formatter for readers that want it.
try:
    from CORE.logging_config import JSONFormatter  # noqa: F401
except ImportError:
    note_failure("logging:L118", None)
