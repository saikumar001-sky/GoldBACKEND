from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI,pool_size=10, max_overflow=5, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        logger.info("DB Closed....")
        db.close()
