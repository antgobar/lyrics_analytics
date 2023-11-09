import os

from flask import Flask

from lyrics_analytics.config import Config, DevelopmentConfig, ProductionConfig
from lyrics_analytics.common.database.queries import AdminQueries


def create_app():
    flask_app = Flask(__name__, instance_relative_config=True)

    env = os.getenv("APP_ENV", "PRODUCTION")

    if env == "DEVELOPMENT":
        flask_app.config.from_object(DevelopmentConfig)
    else:
        flask_app.config.from_object(ProductionConfig)

    flask_app.secret_key = Config.FLASK_SECRET_KEY

    admin_queries = AdminQueries()
    admin_queries.create_admin()

    from lyrics_analytics.api.routes import admin, auth, reports, search, user

    flask_app.register_blueprint(search.bp)
    flask_app.register_blueprint(auth.bp)
    flask_app.register_blueprint(reports.bp)
    flask_app.register_blueprint(admin.bp)
    flask_app.register_blueprint(user.bp)

    flask_app.add_url_rule("/", endpoint="index")

    return flask_app


app = create_app()
app.app_context().push()
