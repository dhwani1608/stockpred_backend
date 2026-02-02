from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

try:
    # Fix PostgreSQL connection string to use psycopg (v3) instead of psycopg2
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql+psycopg2://"):
        db_url = db_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    
    # SQLite needs check_same_thread, PostgreSQL doesn't
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    
    engine = create_engine(db_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")
    engine = None
    SessionLocal = None


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not configured")
        db.close()
