import json

from pika import BlockingConnection, ConnectionParameters

from worker.config import Config
from worker.genius import GeniusService
from worker.tasks import get_artist_songs, search_artists


def provide_handle_search_artists(service: GeniusService):
    def handle_search_artists(ch, method, properties, body: str):
        try:
            message = json.loads(body)
            search_artists(service, **message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error in search_artists: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return handle_search_artists


def provide_handle_get_artist_songs(service: GeniusService, store):
    def handle_get_artist_songs(ch, method, properties, body):
        try:
            message = json.loads(body)
            songs = get_artist_songs(service, **message)
            store.save_songs(songs)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error in get_artist_songs: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return handle_get_artist_songs


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


def consume():
    connection = BlockingConnection(ConnectionParameters(host=Config.RABBITMQ_HOST))
    channel = connection.channel()

    # Declare both queues
    channel.queue_declare(queue=Config.QUEUE_SEARCH, durable=True)
    channel.queue_declare(queue=Config.QUEUE_GET_SONGS, durable=True)

    channel.basic_qos(prefetch_count=1)

    # Bind a consumer for each queue
    channel.basic_consume(
        queue=Config.QUEUE_SEARCH, on_message_callback=handle_search_artists
    )
    channel.basic_consume(
        queue=Config.QUEUE_GET_SONGS, on_message_callback=handle_get_artist_songs
    )

    print("[*] Waiting for messages in both queues. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted")
        channel.stop_consuming()
    finally:
        connection.close()
