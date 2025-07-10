import json

from pika import BlockingConnection, ConnectionParameters

from worker.tasks import get_artist_songs, search_artists

RABBITMQ_HOST = "localhost"

QUEUE_SEARCH = "search_artists_queue"
QUEUE_GET_SONGS = "get_artist_songs_queue"


def handle_search_artists(ch, method, properties, body: str):
    try:
        message = json.loads(body)
        search_artists(**message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error in search_artists: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def handle_get_artist_songs(ch, method, properties, body):
    try:
        message = json.loads(body)
        get_artist_songs(**message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error in get_artist_songs: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    connection = BlockingConnection(ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare both queues
    channel.queue_declare(queue=QUEUE_SEARCH, durable=True)
    channel.queue_declare(queue=QUEUE_GET_SONGS, durable=True)

    channel.basic_qos(prefetch_count=1)

    # Bind a consumer for each queue
    channel.basic_consume(queue=QUEUE_SEARCH, on_message_callback=handle_search_artists)
    channel.basic_consume(
        queue=QUEUE_GET_SONGS, on_message_callback=handle_get_artist_songs
    )

    print("[*] Waiting for messages in both queues. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
