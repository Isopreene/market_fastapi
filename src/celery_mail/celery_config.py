import os
from celery import Celery

CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL",
                                        "amqp://user:pass@localhost:15672//")
CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")

celery_app = Celery(__name__,
                    broker=os.getenv("CELERY_BROKER_URL"),
                    backend=os.getenv("CELERY_RESULT_BACKEND"))

celery_app.conf.update(
    imports=['src.app.router.mail'], # path to your celery_mail tasks
    # file
    broker_connection_retry_on_startup=True,
    task_track_started=True)