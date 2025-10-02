# app/db.py
from sqlmodel import SQLModel, create_engine, Session
from .core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

def init_db():
    from . import models  # ensure models are imported for table creation
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
