from __future__ import annotations

import traceback as tb
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone
from huey.contrib.djhuey import HUEY
from huey.signals import (
    SIGNAL_COMPLETE,
    SIGNAL_ERROR,
    SIGNAL_EXECUTING,
    SIGNAL_INTERRUPTED,
    SIGNAL_RETRYING,
    SIGNAL_REVOKED,
)

from .models import HueyTaskAttempt


def _safe_repr(value, limit: int = 2000) -> str:
    try:
        s = repr(value)
    except Exception:
        return "<unrepr-able>"
    if len(s) > limit:
        return s[: limit - 3] + "..."
    return s


def _task_name(task) -> str:
    # Huey task wrapper name is usually stable; keep defensive.
    return (
        getattr(task, "name", "")
        or getattr(task, "task_name", "")
        or task.__class__.__name__
    )


def _task_eta(task):
    eta = getattr(task, "eta", None) or getattr(task, "execute_time", None)
    if isinstance(eta, datetime):
        # normalize to aware, in UTC
        if eta.tzinfo is None:
            return eta.replace(tzinfo=dt_timezone.utc)
        return eta.astimezone(dt_timezone.utc)
    return None


def _upsert_attempt(task, status: str, **fields):
    # Single-row “current attempt” strategy keyed by task_id + started_at bucket:
    # For simplicity: just create new rows for EXECUTING, then update the latest row for completion/error.
    task_id = str(getattr(task, "id", "") or getattr(task, "task_id", ""))

    if status == HueyTaskAttempt.Status.EXECUTING:
        HueyTaskAttempt.objects.create(
            task_id=task_id,
            task_name=_task_name(task),
            status=status,
            started_at=timezone.now(),
            retries=getattr(task, "retries", None),
            eta=_task_eta(task),
            args_repr=_safe_repr(getattr(task, "args", None)),
            kwargs_repr=_safe_repr(getattr(task, "kwargs", None)),
        )
        return

    # For terminal-ish signals, update the most recent attempt row.
    attempt = (
        HueyTaskAttempt.objects.filter(task_id=task_id).order_by("-created_at").first()
    )
    if not attempt:
        attempt = HueyTaskAttempt.objects.create(
            task_id=task_id,
            task_name=_task_name(task),
            status=status,
            started_at=None,
        )

    now = timezone.now()
    attempt.status = status
    if attempt.started_at and not attempt.finished_at:
        attempt.finished_at = now
        attempt.duration_ms = int(
            (attempt.finished_at - attempt.started_at).total_seconds() * 1000
        )

    for k, v in fields.items():
        setattr(attempt, k, v)

    attempt.retries = getattr(task, "retries", attempt.retries)
    attempt.save(
        update_fields=[
            "status",
            "finished_at",
            "duration_ms",
            "retries",
            "exc_type",
            "exc_message",
            "traceback",
        ]
    )


@HUEY.signal(SIGNAL_EXECUTING)
def on_executing(signal, task):
    _upsert_attempt(task, HueyTaskAttempt.Status.EXECUTING)


@HUEY.signal(SIGNAL_COMPLETE)
def on_complete(signal, task):
    _upsert_attempt(task, HueyTaskAttempt.Status.COMPLETE)


@HUEY.signal(SIGNAL_RETRYING)
def on_retrying(signal, task):
    _upsert_attempt(task, HueyTaskAttempt.Status.RETRYING)


@HUEY.signal(SIGNAL_REVOKED)
def on_revoked(signal, task):
    _upsert_attempt(task, HueyTaskAttempt.Status.REVOKED)


@HUEY.signal(SIGNAL_INTERRUPTED)
def on_interrupted(signal, task):
    _upsert_attempt(task, HueyTaskAttempt.Status.INTERRUPTED)


@HUEY.signal(SIGNAL_ERROR)
def on_error(signal, task, exc=None):
    exc_type = type(exc).__name__ if exc else ""
    exc_message = str(exc) if exc else ""
    trace = (
        "".join(tb.format_exception(type(exc), exc, exc.__traceback__)) if exc else ""
    )
    _upsert_attempt(
        task,
        HueyTaskAttempt.Status.ERROR,
        exc_type=exc_type,
        exc_message=exc_message,
        traceback=trace,
    )
