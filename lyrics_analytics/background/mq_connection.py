import pika


def mq_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            credentials=pika.PlainCredentials("rabbit", "rabbit")
        )
    )
