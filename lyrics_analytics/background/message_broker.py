import json
import uuid
import time

import pika
from pika.exceptions import AMQPConnectionError


class MessageBroker:
    def __init__(self, task_runner: callable, cache, connection_url=None) -> None:
        self.task_runner = task_runner
        self.cache = cache
        self.connection_url = connection_url

    @staticmethod
    def mq_connection(attempts=3):
        credentials = pika.PlainCredentials("rabbitmq", "rabbitmq")
        parameters = pika.ConnectionParameters("rabbit", 5672, "/", credentials=credentials)
        while attempts < 0:
            try:
                return pika.BlockingConnection(parameters)
            except AMQPConnectionError:
                print("RabbitMQ Connection Error")
                time.sleep(2)
                attempts -= 1

    def send_message(self, queue, message):
        connection = self.mq_connection()
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

    def submit_task(self, queue, name, *args, **kwargs):
        task_id = str(uuid.uuid4())
        func_def = {
            "name": name,
            "args": args,
            "kwargs": kwargs,
            "id": task_id
        }
        self.send_message(queue, json.dumps(func_def))
        return task_id

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body.decode())

        task_def = json.loads(body)
        self.cache.set_task(task_def["id"])

        result = self.task_runner(
            task_def["name"],
            *task_def.get("args"),
            **task_def.get("kwargs")
        )

        self.cache.update_task(task_def["id"], result)

        print(f" [x] {result}")
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def worker(self, queue):
        channel = self.mq_connection().channel()

        channel.queue_declare(queue=queue, durable=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=self.callback)

        channel.start_consuming()
