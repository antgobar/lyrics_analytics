import json
import uuid

import pika

from lyrics_analytics.background.register import REGISTERED_TASKS


def run_task(name, *args, **kwargs):
    tasks = {task.__name__: task for task in REGISTERED_TASKS}
    return tasks[name](*args, **kwargs)


class RabbitService:

    @classmethod
    def mq_connection(cls):
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=pika.PlainCredentials("rabbit", "rabbit")
            )
        )

    @classmethod
    def send_message(cls, queue, message):
        connection = cls.mq_connection()
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

    @classmethod
    def submit_task(cls, name, *args, **kwargs):
        task_id = str(uuid.uuid4())
        func_def = {
            "name": name,
            "args": args,
            "kwargs": kwargs,
            "id": task_id
        }
        cls.send_message("task_queue", json.dumps(func_def))
        return task_id

    @classmethod
    def callback(cls, ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        task_def = json.loads(body)
        task_id = task_def["id"]
        result = run_task(task_def["name"], *task_def.get("args"), **task_def.get("kwargs"))
        print(f" [x] {result}")
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    @classmethod
    def get_result(cls, task_id):
        return None

    @classmethod
    def worker(cls, queue):
        channel = cls.mq_connection().channel()

        channel.queue_declare(queue=queue, durable=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=cls.callback)

        channel.start_consuming()
