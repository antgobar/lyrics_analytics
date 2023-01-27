import json
import time

import pika
from pika.exceptions import AMQPConnectionError


class MessageBroker:
    def __init__(self, url=None, callback_handler: callable=None) -> None:
        self.url = url
        self.connection = self.connection()
        self.callback_handler = callback_handler if callback_handler else lambda x: x

    def connection(self, attempts=3):
        parameters = pika.URLParameters(self.url)
        while attempts > 0:
            try:
                connection = pika.BlockingConnection(parameters)
                if connection is None:
                    print("CONNECTION is None")
                    time.sleep(1)
                    continue
                return connection
            except AMQPConnectionError:
                attempts -= 1
                print(f"AMQPConnectionError raised - attempts left {attempts}")
                time.sleep(1)

    def send_message(self, queue, message):
        connection = self.connection
        channel = connection.channel()

        channel.queue_declare(queue=queue, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        print(" [x] Sent %r" % message)
        connection.close()

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        result = self.callback_handler(body)
        print(f" [x] {result}")
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consumer(self, queue):
        connection = self.connection
        channel = connection.channel()
        print(' [*] Waiting for messages. To exit press CTRL+C')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=self.callback)

        channel.start_consuming()
