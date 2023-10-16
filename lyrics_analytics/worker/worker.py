from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name)
    celery_config = app.config["CELERY_CONFIG"]
    print(celery_config)
    celery.conf.update(celery_config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
