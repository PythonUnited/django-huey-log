import pytest

from example.tasks import failure_task, retry_configured_task, success_task

from ..models import HueyTaskAttempt


@pytest.mark.django_db
def test_task_logging_success():
    # Trigger the task (calling .task_id usually triggers huey logic in testing)
    success_task("test-user")

    # Check if an attempt was logged
    attempt = HueyTaskAttempt.objects.first()
    assert attempt is not None
    assert attempt.task_name == "success_task"


@pytest.mark.django_db
def test_task_logging_failure():
    # Trigger a failing task.
    # We don't necessarily need pytest.raises if Huey handles the exception internally,
    # we just need to verify that the SIGNAL_ERROR was caught and logged.
    failure_task()

    # Check if a failure attempt was logged
    attempt = HueyTaskAttempt.objects.filter(task_name="failure_task").first()
    assert attempt is not None
    assert attempt.status == HueyTaskAttempt.Status.ERROR
    assert attempt.exc_type == "ValueError"
    assert "This task was designed to fail!" in attempt.exc_message
    assert len(attempt.traceback) > 0


@pytest.mark.django_db
def test_task_logging_arguments():
    # Test complex argument capturing.
    # Note: 'name' is a keyword argument here, so it goes into kwargs_repr.
    success_task(name={"complex": [1, 2, 3]})

    attempt = HueyTaskAttempt.objects.filter(task_name="success_task").first()
    assert "{'complex': [1, 2, 3]}" in attempt.kwargs_repr


@pytest.mark.django_db
def test_retries_remaining_defaults_to_zero_without_retries_kwarg():
    # success_task is defined with plain @task(), i.e. huey's retries=0
    # default. retries_remaining reflects that budget, not "attempts made".
    success_task("test-user")

    attempt = HueyTaskAttempt.objects.filter(task_name="success_task").first()
    assert attempt.retries_remaining == 0


@pytest.mark.django_db
def test_retries_remaining_reflects_configured_budget_on_first_success():
    # retry_configured_task is defined with @task(retries=3). Since it
    # succeeds on the first attempt, no retry ever fires, so the logged
    # retries_remaining is still the full configured budget, not zero.
    retry_configured_task()

    attempt = HueyTaskAttempt.objects.filter(task_name="retry_configured_task").first()
    assert attempt.retries_remaining == 3
