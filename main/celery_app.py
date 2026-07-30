from celery import Celery
from main import app

celery = Celery(
    app.import_name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"],
)

import tasks

celery.conf.beat_schedule = {
    "publish-outbox-events": {
        "task": "tasks.publish_outbox_events",
        "schedule": 1.0,
    },
}

celery.conf.timezone = "UTC"