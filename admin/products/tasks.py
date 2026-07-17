import requests
from celery import shared_task
from .models import Product
from .producer import publish

@shared_task
def reconcile_products():
    django_products = {p.id: p for p in Product.objects.all()}
    django_ids = set(django_products.keys())

    try:
        flask_response = requests.get("http://main-backend-1:5000/api/products", timeout=5)
        flask_products = flask_response.json()
        flask_ids = {p["id"] for p in flask_products}
    except Exception as e:
        print(f"Reconciliation failed: could not reach Flask - {e}")
        return

    missing_in_flask = django_ids - flask_ids
    extra_in_flask = flask_ids - django_ids

    # republish anything Django has that Flask is missing
    for product_id in missing_in_flask:
        product = django_products[product_id]
        publish('product_created', {
            'id': product.id,
            'title': product.title,
            'image': product.image,
            'likes': product.likes,
        })
        print(f"Re-published missing product {product_id} to Kafka")

    # tell Flask to delete anything it has that Django doesn't recognize
    for product_id in extra_in_flask:
        publish('product_deleted', product_id)
        print(f"Published delete for ghost product {product_id}")

    if not missing_in_flask and not extra_in_flask:
        print("Reconciliation check passed: Django and Flask are in sync")
    django_products = {p.id: p for p in Product.objects.all()}
    django_ids = set(Product.objects.values_list('id', flat=True))

    try:
        flask_response = requests.get("http://main-backend-1:5000/api/products", timeout=5)
        flask_products = flask_response.json()
        flask_ids = {p["id"] for p in flask_products}
    except Exception as e:
        print(f"Reconciliation failed: could not reach Flask - {e}")
        return

    missing_in_flask = django_ids - flask_ids
    extra_in_flask = flask_ids - django_ids

    # republish anything django has the Flask is missing

    for product_id in missing_in_flask:
        product = django_products[product_id]
        publish('product_created', {
            
        })
    if missing_in_flask:
        print(f"DRIFT DETECTED: {len(missing_in_flask)} products in Django missing from Flask: {missing_in_flask}")
    if extra_in_flask:
        print(f"DRIFT DETECTED: {len(extra_in_flask)} products in Flask not in Django (ghosts): {extra_in_flask}")
    if not missing_in_flask and not extra_in_flask:
        print("Reconciliation check passed: Django and Flask are in sync")