from celery import Celery
from celery.schedules import crontab

from .config import settings

celery_app = Celery("echobrief", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "aggregate-news-daily": {
        "task": "app.tasks.news_aggregation.aggregate_news_task",
        "schedule": crontab(minute="*/1"),  # Every 1 minute for testing
    },
    "generate-daily-podcasts": {
        "task": "app.tasks.podcast_generation.generate_daily_podcasts",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
    },
}

celery_app.conf.imports = (
    "app.tasks.news_aggregation",
    "app.tasks.podcast_generation",
    "app.tasks.email_tasks",
    "app.tasks.subscription_management",
)
