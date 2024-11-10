#!/bin/bash

echo 'alembic upgrade head'
alembic upgrade head
echo 'celery --app src.celery_mail.celery_config.celery_app worker --detach --loglevel=info --pool=solo'
celery --app src.celery_mail.celery_config.celery_app worker --detach --loglevel=info --pool=solo
echo 'uvicorn src.app.main --reload --host 0.0.0.0 --port 8000'
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000