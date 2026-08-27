from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "ors",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    enable_utc=False,
    timezone=settings.celery_timezone,
    task_track_started=True,
)
