from django.contrib import admin

from .models import HueyTaskAttempt


@admin.register(HueyTaskAttempt)
class HueyTaskAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "task_name",
        "task_id",
        "status",
        "retries",
        "duration_ms",
    )
    list_filter = ("status", "task_name", "created_at")
    search_fields = ("task_id", "task_name", "exc_message", "traceback")
    readonly_fields = [f.name for f in HueyTaskAttempt._meta.fields]

    def has_add_permission(self, request):
        return False
