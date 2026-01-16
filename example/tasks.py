from huey.contrib.djhuey import task, db_task
import time

@task()
def success_task(name):
    print(f"Hello {name}!")
    time.sleep(1)
    return f"Done {name}"

@task()
def failure_task():
    time.sleep(0.5)
    raise ValueError("This task was designed to fail!")