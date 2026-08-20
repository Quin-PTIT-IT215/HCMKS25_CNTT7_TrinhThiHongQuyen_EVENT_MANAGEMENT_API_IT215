from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


DATASE_URL = settings.DATABASE_URL
engine = create_engine(DATASE_URL)

SessionLocal = sessionmaker(
    autocommit= False,
    autoflush= False,
    bind= engine
)

class Base(DeclarativeBase):
    pass

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()