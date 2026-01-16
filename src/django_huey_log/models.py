from __future__ import annotations

from django.db import models
from django.utils import timezone


class HueyTaskAttempt(models.Model):
    class Status(models.TextChoices):
        EXECUTING = "executing"
        COMPLETE = "complete"
        ERROR = "error"
        RETRYING = "retrying"
        REVOKED = "revoked"
        LOCKED = "locked"
        EXPIRED = "expired"
        INTERRUPTED = "interrupted"
        OTHER = "other"

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    # Huey identifiers
    task_id = models.CharField(max_length=64, db_index=True)
    task_name = models.CharField(max_length=255, db_index=True, blank=True)

    # Attempt metadata
    retries = models.IntegerField(null=True, blank=True)
    eta = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=32, choices=Status.choices, db_index=True)

    started_at = models.DateTimeField(null=True, blank=True, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True, db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    # Minimal payload (avoid huge data)
    args_repr = models.TextField(blank=True)
    kwargs_repr = models.TextField(blank=True)

    # Error capture
    exc_type = models.CharField(max_length=255, blank=True)
    exc_message = models.TextField(blank=True)
    traceback = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["task_name", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.task_name or 'task'} [{self.task_id}] {self.status}"
