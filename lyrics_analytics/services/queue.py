import uuid
import json

import pika


def producer(host, queue, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    message_id = str(uuid.uuid4())
    body = {
        "id": message_id,
        "message": message
    }
    channel.basic_publish(exchange='', routing_key='my_queue', body=json.dumps(body).encode())


def consumer(host: str, queue: str, callback: callable):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue=queue)

    def on_callback(ch, method, properties, body):
        callback(body)

    channel.basic_consume(queue='my_queue', on_message_callback=on_callback, auto_ack=True)
    channel.start_consuming()
