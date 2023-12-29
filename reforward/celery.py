import os
from django.db import connection

from celery import Celery, Task


class DjangoCeleryTask(Task):
    """
    Implements after return hook to close the invalid connection.
    This way, django is forced to serve a new connection for the next
    task.
    """

    abstract = True

    def after_return(self, *args, **kwargs):
        connection.close()


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reforward.settings")

app = Celery(
    "reforward",
    task_cls="reforward.celery.DjangoCeleryTask",
    broker_connection_retry_on_startup=True,
)


app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
app.conf.enable_utc = False


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
