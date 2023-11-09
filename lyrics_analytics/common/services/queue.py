import uuid
import json
import logging

import pika

from lyrics_analytics.config import Config


logging.basicConfig(level=logging.INFO)
QUEUE = "artist_data"
HOST = Config.MESSAGE_BROKER_URL


def get_channel():
    params = pika.URLParameters(HOST)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE)
    return channel


def producer(message):
    channel = get_channel()
    message_id = str(uuid.uuid4())
    body = {
        "id": message_id,
        "message": message
    }
    channel.basic_publish(exchange="", routing_key=QUEUE, body=json.dumps(body).encode())
    logging.info(f"[x] Sent message {body}")


def consumer(callback: callable):
    channel = get_channel()

    def on_callback(ch, method, properties, body):
        parsed = json.loads(body.decode())
        logging.info(f"[x] Message Received: {body}")
        try:
            callback(parsed["message"])
        except Exception as e:
            logging.error("Error parsing message:")
            logging.error(parsed)
            logging.error(e)

    channel.basic_consume(queue=QUEUE, on_message_callback=on_callback, auto_ack=True)
    logging.info("[x] Waiting for message")
    channel.start_consuming()
