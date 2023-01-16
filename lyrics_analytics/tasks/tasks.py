import os

from celery import Celery


def make_celery(app):
    app.config.update(
        CELERY_CONFIG={
            "broker_url": os.environ.get("CELERY_BROKER_URL", "amqp://localhost:5672"),
            "result_backend": os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379"),
        }
    )
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
