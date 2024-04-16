import os
from datetime import timedelta

# database config
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# security config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRATION = timedelta(minutes=5)
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)
ONE_TIME_TOKEN_EXPIRATION = timedelta(minutes=3)

# email config
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


TORTOISE_CONFIG = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:" f"{DB_PORT}/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
