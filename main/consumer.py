# consumer.py
import pika, json
import os
from main import Product, db

params = pika.URLParameters(os.environ.get("CLOUDAMQP_URL"))
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='product_events')

from main import app, Product, db

def callback(ch, method, properties, body):
    print("Received in admin")
    data = json.loads(body)
    print(data)

    with app.app_context():
        if properties.type == 'product_created':
            product = Product(id=data['id'], title=data['title'], image=data['image'])
            db.session.add(product)
            db.session.commit()
            print("Product Created")

        elif properties.type == 'product_updated':
            product = Product.query.get(data['id'])
            product.title = data['title']
            product.image = data['image']
            db.session.commit()
            print("Product Updated")

        elif properties.type == 'product_deleted':
            product = Product.query.get(data)
            db.session.delete(product)
            db.session.commit()
            print("Product deleted")
            
channel.basic_consume(queue='product_events', on_message_callback=callback, auto_ack=True)

print('Started consuming')
channel.start_consuming()