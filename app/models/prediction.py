from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(50), index=True)
    direction = Column(String(10))  # UP or DOWN
    confidence = Column(Float)
    signal = Column(String(20))  # BUY, SELL, NO_TRADE
    horizon_days = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Input features stored for reference
    close_price = Column(Float)
    return_1 = Column(Float)
    return_5 = Column(Float)
    ma_10 = Column(Float)
    ma_20 = Column(Float)
    ema_10 = Column(Float)
    volatility_10 = Column(Float)
    lag_1 = Column(Float)
    lag_5 = Column(Float)
