from lyrics_analytics.background.rabbitmq import RabbitService


if __name__ == "__main__":
    RabbitService.worker("task_queue")
