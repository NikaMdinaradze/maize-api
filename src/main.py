from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from src.db import db_url
from src.settings import DATABASE_MODELS

app = FastAPI()

register_tortoise(
    app,
    db_url=db_url,
    modules={"models": DATABASE_MODELS},
    generate_schemas=True,
    add_exception_handlers=True,
)
