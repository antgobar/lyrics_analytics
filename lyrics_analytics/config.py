import os

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_ENV = os.getenv("APP_ENV")
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    CELERY_CONFIG = {
        "broker_url": os.environ.get("BROKER_URL"),
        "result_backend": os.environ.get("RESULT_BACKEND"),
    }
    MONGO_URI = os.getenv("MONGO_URI")
    GENIUS_CLIENT_ACCESS_TOKEN = os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")
    PEPPER = os.getenv("PEPPER")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    GENIUS_BASE_URL = os.getenv("GENIUS_BASE_URL")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "LyricStats")
    MONGO_URI_PROD = os.getenv("MONGO_URI_PROD")


class DevelopmentConfig(Config):
    DEBUG = True
    APP_ENV = "DEV"


class TestingConfig(Config):
    TESTING = True
    APP_ENV = "TEST"


class ProductionConfig(Config):
    APP_ENV = "PROD"
