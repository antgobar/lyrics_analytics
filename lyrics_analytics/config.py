import os
from pathlib import Path

from dotenv import load_dotenv


dotenv_path = Path(".prod.env")
load_dotenv(dotenv_path=dotenv_path)


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


class DevelopmentConfig(Config):
    DEBUG = True
    APP_ENV = "DEVELOPMENT"


class ProductionConfig(Config):
    APP_ENV = "PRODUCTION"
