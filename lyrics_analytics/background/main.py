import time

from lyrics_analytics.background.rabbitmq import RabbitService


task_id = RabbitService.submit_task(
    "get_artist_songs",
    8351
)

while True:
    result = RabbitService.get_result(task_id)
    print(result)
    if result.decode() != "PENDING":
        break

    time.sleep(1)
