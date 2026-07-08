import pika
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "admin.settings")
django.setup()
import json
from products.models import Product

params = pika.URLParameters(os.environ.get("CLOUDAMQP_URL"))
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='like_events')

from django.core.exceptions import ObjectDoesNotExist

def callback(ch, method, properties, body):
    print(f"Event type: {properties.type}")
    product_id = json.loads(body)
    print(product_id)

    try:
        product = Product.objects.get(id=product_id)
        product.likes = product.likes + 1
        product.save()
        print('Product likes increased')
    except Product.DoesNotExist:
        print(f"Product {product_id} not found, skipping")

channel.basic_consume(queue='like_events', on_message_callback=callback, auto_ack=True)
print('Started consuming')
channel.start_consuming()