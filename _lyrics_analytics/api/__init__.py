import os

from flask import Flask

from _lyrics_analytics.config import Config, DevelopmentConfig, ProductionConfig
from _lyrics_analytics.worker.worker import make_celery
from _lyrics_analytics.database.queries import AdminQueries


def create_app():
    admin_queries = AdminQueries()
    admin_queries.create_admin()

    flask_app = Flask(__name__, instance_relative_config=True)

    env = os.getenv("APP_ENV", "PRODUCTION")
    if env == "DEVELOPMENT":
        flask_app.config.from_object(DevelopmentConfig)
    else:
        flask_app.config.from_object(ProductionConfig)

    flask_app.secret_key = Config.FLASK_SECRET_KEY

    celery_app = make_celery(flask_app)
    celery_app.set_default()

    from _lyrics_analytics.api.routes import admin, auth, reports, search, user

    flask_app.register_blueprint(search.bp)
    flask_app.register_blueprint(auth.bp)
    flask_app.register_blueprint(reports.bp)
    flask_app.register_blueprint(admin.bp)
    flask_app.register_blueprint(user.bp)

    flask_app.add_url_rule("/", endpoint="index")

    return flask_app, celery_app


app, celery = create_app()
app.app_context().push()
