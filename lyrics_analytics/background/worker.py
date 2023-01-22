import json

from lyrics_analytics.background.mq_connection import mq_connection
from lyrics_analytics.background.task import TaskRegister


task_register = TaskRegister()


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    # func_def = json.loads(body.decode())
    # result = task_register.run_task(func_def["name"], func_def["args"], func_def["kwargs"])
    # print(f" [x] {result}")
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def worker(queue):
    channel = mq_connection().channel()

    channel.queue_declare(queue=queue, durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)

    channel.start_consuming()


if __name__ == '__main__':
    worker("task_queue")
