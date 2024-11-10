from celery import Celery
from config import settings

CELERY_BROKER_URL = (f"amqp://{settings.RABBITMQ_DEFAULT_USER}:"
                     f"{settings.RABBITMQ_DEFAULT_PASS}@"
                     f"{settings.RABBITMQ_DEFAULT_HOST}:"
                     f"{settings.RABBITMQ_DEFAULT_PORT}//")

CELERY_RESULT_BACKEND = "rpc://"

celery_app = Celery(__name__,
                    broker=CELERY_BROKER_URL,
                    backend=CELERY_RESULT_BACKEND)

celery_app.conf.update(
    imports=['src.celery_mail.tasks'],
    broker_connection_retry_on_startup=True,
    task_track_started=True)
