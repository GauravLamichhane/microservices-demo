from celery import Celery
from celery.signals import worker_process_init
from main import app

celery = Celery(
    app.import_name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"],
)
import tasks

@worker_process_init.connect
def init_worker(**kwargs):
    from main import db
    db.engine.dispose()

celery.conf.beat_schedule = {
    "publish-outbox-events": {
        "task": "tasks.publish_outbox_events",
        "schedule": 1.0,
    },
}

celery.conf.timezone = "UTC"