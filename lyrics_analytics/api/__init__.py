import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "lyrics_analytics.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/test")
    def in_test():
        return {"lyrics_analytics: test_endpoint"}, 200

    from . import search

    app.register_blueprint(search.bp)
    app.add_url_rule("/", endpoint='index')

    return app
