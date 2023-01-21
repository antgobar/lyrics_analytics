import pika


def mq_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            credentials=pika.PlainCredentials("rabbit", "rabbit")
        )
    )


def send_message(queue, message):
    connection = mq_connection()
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


if __name__ == "__main__":
    send_message("artist_name_query", "megadeth")
