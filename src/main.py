import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from src.endpoints import auth, profile

app = FastAPI(
    title="Maize API",
    description="MVP api for maize",
    version="0.01",
    default_response_class=ORJSONResponse,
)

app.include_router(auth.router)
app.include_router(profile.router)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://maize.vercel.app/",  # TODO: front end url should be dynamic from .env
    "https://maize.vercel.app",
    "http://13.60.35.76",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check and create 'media' directory if it doesn't exist
if not os.path.exists("media/profile"):
    os.makedirs("media/profile")
app.mount("/media/profile", StaticFiles(directory="media/profile"), name="media-profile")
