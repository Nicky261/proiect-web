import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL-ul bazei de date il luam din .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Factory pentru sesiuni
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Dependency pentru FastAPI (yield session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
