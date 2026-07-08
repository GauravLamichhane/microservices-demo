import pika
import json
import os

def publish(method, body):
    params = pika.URLParameters(os.environ.get("CLOUDAMQP_URL"))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='like_events')

    properties = pika.BasicProperties(type=method)
    channel.basic_publish(
        exchange='',
        routing_key='like_events',
        body=json.dumps(body),
        properties=properties
    )
    connection.close()