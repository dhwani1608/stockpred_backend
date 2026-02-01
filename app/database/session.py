from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

try:
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")
    engine = None
    SessionLocal = None


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not configured")
        db.close()
