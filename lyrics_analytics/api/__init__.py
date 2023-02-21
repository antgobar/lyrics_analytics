import os

from flask import Flask

from lyrics_analytics.backend.worker import make_celery


def create_app(test_config=None):
    flaskapp = Flask(__name__, instance_relative_config=True)
    flaskapp.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(flaskapp.instance_path, "lyrics_analytics.sqlite"),
    )

    flaskapp.config["CELERY_CONFIG"] = {
        "broker_url": os.environ.get("BROKER_URL", "amqp://localhost:5672"),
        "result_backend": os.environ.get("RESULT_BACKEND", "redis://localhost:6379")
    }

    @flaskapp.route("/test")
    def in_test():
        return {"lyrics_analytics: test_endpoint"}, 200

    celeryapp = make_celery(flaskapp)
    celeryapp.set_default()

    from lyrics_analytics.api import search, auth, reports

    flaskapp.register_blueprint(search.bp)
    flaskapp.register_blueprint(auth.bp)
    flaskapp.register_blueprint(reports.bp)


    flaskapp.add_url_rule("/", endpoint="index")

    return flaskapp, celeryapp


app, celery = create_app()
app.app_context().push()
