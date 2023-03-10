import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", default="some key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_CONFIG = {
        "broker_url": os.environ.get("BROKER_URL", "amqp://localhost:5672"),
        "result_backend": os.environ.get("RESULT_BACKEND", "redis://localhost:6379")
    }
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(basedir, "lyrics-analytics.db"))
    MONGO_HOST = os.getenv("MONGO_HOST")
    MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    GENIUS_CLIENT_ACCESS_TOKEN = os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    FLASK_ENV = "production"
