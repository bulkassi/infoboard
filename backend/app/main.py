from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from sqlmodel import Session

from app.core.db import engine, init_db
from app.crud import seed_admin_user, seed_about_content, seed_boards
import logging

app = FastAPI(title="Infoboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def startup_seed() -> None:
    try:
        init_db()
        with Session(engine) as session:
            seed_boards(session)
            seed_about_content(session)
            seed_admin_user(
                session, settings.FIRST_SUPERUSER, settings.FIRST_SUPERUSER_PASSWORD
            )
    except Exception as exc:  # pragma: no cover - prevents tests from failing on missing DB
        logging.warning("Database initialization/seeding skipped: %s", exc)
