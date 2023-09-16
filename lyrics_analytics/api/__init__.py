from flask import Flask

from lyrics_analytics.backend.worker import make_celery
from lyrics_analytics.config import Config, DevelopmentConfig


def create_app(test_config=None):
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config.from_object(DevelopmentConfig)
    flask_app.secret_key = Config.FLASK_SECRET_KEY

    celery_app = make_celery(flask_app)
    celery_app.set_default()

    if test_config is None:
        flask_app.config.from_pyfile("config.py", silent=True)
    else:
        flask_app.config.from_mapping(test_config)

    from lyrics_analytics.api.routes import reports
    from lyrics_analytics.api.routes import search
    from lyrics_analytics.api.routes import admin
    from lyrics_analytics.api.routes import auth

    flask_app.register_blueprint(search.bp)
    flask_app.register_blueprint(auth.bp)
    flask_app.register_blueprint(reports.bp)
    flask_app.register_blueprint(admin.bp)

    flask_app.add_url_rule("/", endpoint="index")

    return flask_app, celery_app


app, celery = create_app()
app.app_context().push()
