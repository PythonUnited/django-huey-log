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
   uv add django-huey-log
   ```

2. Add `huey_log` to your `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       "huey_log",
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

## License

MIT