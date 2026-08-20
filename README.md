# django-huey-log

Log and monitor [Huey](https://huey.readthedocs.io/en/latest/) task attempts directly in your Django admin.

`django-huey-log` automatically captures task execution details, including status, duration, and error tracebacks, providing a searchable history of your background jobs without needing to dig through log files.

## Features

- **Automated Tracking**: Hooks into Huey signals to record `EXECUTING`, `COMPLETE`, `ERROR`, `RETRYING`, and `REVOKED` states.
- **Detailed Visibility**: Logs start/end times, duration (ms), task arguments (repr), and full exception tracebacks.
- **Django Admin Integration**: View, filter, and search task attempts within the Django admin interface.
- **Minimal Overhead**: Only records metadata; avoids large payload storage.

## Installation

1. Install the package using [uv](https://docs.astral.sh/uv/):
   ```bash
   uv add git+https://github.com/PythonUnited/django-huey-log.git
   ```

2. Add `huey_log` to your `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       "django_huey_log",
       # ...
   ]
   ```

3. Run migrations to create the log tables:
   ```bash
   uv run manage.py migrate
   ```

## Configuration

The package works automatically once added to `INSTALLED_APPS` and requires `django-huey` to be configured in your project. It connects to the `HUEY` instance defined in your settings.

## Usage

Once installed, navigate to the **Huey Task Attempts** section in your Django Admin. You can:
- Filter tasks by status (e.g., failed, retrying).
- Search by task name or task ID.
- Inspect the traceback for failed tasks to debug issues quickly.

### Reading `retries_remaining`

This is a snapshot of huey's own `task.retries` at the time of the attempt --
the number of retries still available, not how many attempts have happened.
It only decrements when a retry actually fires. A task defined with
`@task(retries=8)` that succeeds on its very first try will log
`retries_remaining: 8` for that single attempt; a task defined with no
`retries=` kwarg (huey's default is `0`) always logs `retries_remaining: 0`,
even though it ran successfully and was never retried.

## License

MIT