from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app import crud
from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine, init_db

app = FastAPI(title="Infoboard API")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with Session(engine) as session:
        crud.seed_boards(session)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
