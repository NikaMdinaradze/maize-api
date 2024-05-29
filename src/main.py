from fastapi import FastAPI

from src.endpoints import auth
from src.settings import init_db

app = FastAPI()

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "root url"}


@app.on_event("startup")
async def on_startup():
    await init_db()
