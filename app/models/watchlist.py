from uuid import uuid4

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from app.database.base import Base


watchlist_symbols = Table(
    "watchlist_symbols",
    Base.metadata,
    Column("watchlist_id", String(50), ForeignKey("watchlists.id"), primary_key=True),
    Column("symbol", String(50), primary_key=True),
)


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(String(50), primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
