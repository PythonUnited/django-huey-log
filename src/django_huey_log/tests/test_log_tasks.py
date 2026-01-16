import pytest
from ..models import HueyTaskAttempt
from example.tasks import success_task


@pytest.mark.django_db
def test_task_logging_success():
    # Trigger the task (calling .task_id usually triggers huey logic in testing)
    task_result = success_task("test-user")

    # Check if an attempt was logged
    attempt = HueyTaskAttempt.objects.first()
    assert attempt is not None
    assert attempt.task_name == "example.tasks.success_task"
    # Note: In synchronous testing, you might need to manually trigger signals
    # depending on your HUEY configuration in tests.