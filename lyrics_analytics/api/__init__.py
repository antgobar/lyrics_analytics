from flask import Flask

from lyrics_analytics.backend.worker import make_celery
from lyrics_analytics.backend import db
from lyrics_analytics import config


def create_app(test_config=None):
    flaskapp = Flask(__name__, instance_relative_config=True)
    flaskapp.config.from_object(config.DevelopmentConfig)

    celeryapp = make_celery(flaskapp)
    celeryapp.set_default()

    @flaskapp.context_processor
    def inject_data():
        artists_collection = db.get_collection("lyrics_analytics", "artists")
        count = artists_collection.count_documents({})
        return dict(reports_ready=count)

    from lyrics_analytics.api.routes import reports
    from lyrics_analytics.api.routes import search
    from lyrics_analytics.api.routes import admin
    from lyrics_analytics.api.routes import auth

    flaskapp.register_blueprint(search.bp)
    flaskapp.register_blueprint(auth.bp)
    flaskapp.register_blueprint(reports.bp)
    flaskapp.register_blueprint(admin.bp)

    flaskapp.add_url_rule("/", endpoint="index")

    return flaskapp, celeryapp


app, celery = create_app()
app.app_context().push()
