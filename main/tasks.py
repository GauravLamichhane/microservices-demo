from celery import shared_task
from main import app, db, PublishedEvent
from producer import publish


@shared_task
def publish_outbox_events():
    with app.app_context():
        events = PublishedEvent.query.filter_by(is_consumed=False).all()

        print(f"Found {len(events)} unpublished events")

        for event in events:
            print(f"Publishing event {event.id}")

            try:
                publish(event.extra["type"], event.payload)

                event.is_consumed = True
                print(f"Published event {event.id}")

            except Exception as e:
                print(f"Failed event {event.id}: {e}")

        db.session.commit()
        print("Commit complete")