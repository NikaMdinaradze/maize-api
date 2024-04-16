from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from src.endpoints import auth, user
from src.settings import TORTOISE_CONFIG

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "root url"}


register_tortoise(
    app,
    db_url=TORTOISE_CONFIG["connections"]["default"],
    modules={"models": ["src.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
