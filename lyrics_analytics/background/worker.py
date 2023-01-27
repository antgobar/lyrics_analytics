from lyrics_analytics.background.task import Task

task = Task(broker_url="amqp://guest:guest@localhost:5672/", cache_host="localhost")
task.start_worker()