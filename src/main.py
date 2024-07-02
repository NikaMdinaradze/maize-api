from fastapi import FastAPI

from src.endpoints import auth

app = FastAPI(title="Maize API", description="MVP api for maize", version="0.01")

app.include_router(auth.router)
