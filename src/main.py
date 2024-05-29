from fastapi import FastAPI

from src.endpoints import auth
from src.settings import init_db

app = FastAPI(title="Maize API", description="MVP api for maize", version="0.01")

app.include_router(auth.router)


@app.get("/")
def root() -> dict:
    return {"message": "root url"}


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
