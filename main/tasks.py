from celery import shared_task
from main import app, db, PublishedEvent
from producer import publish


@shared_task
def publish_outbox_events():
    with app.app_context():
        events = PublishedEvent.query.filter_by(
            is_consumed=False
        ).all()

        for event in events:
            try:
                publish(
                    event.extra["type"],
                    event.payload,
                )

                event.is_consumed = True

            except Exception as e:
                print(f"Failed to publish event {event.id}: {e}")

        db.session.commit()