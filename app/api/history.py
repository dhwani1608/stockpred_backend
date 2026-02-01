from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.prediction import Prediction
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/predictions")
def get_predictions_history(
    days: int = 30,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recent prediction history."""
    since = datetime.now() - timedelta(days=days)
    predictions = db.query(Prediction).filter(
        Prediction.created_at >= since
    ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return predictions


@router.get("/predictions/{symbol}")
def get_symbol_history(
    symbol: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get prediction history for a specific symbol."""
    predictions = db.query(Prediction).filter(
        Prediction.symbol == symbol.upper()
    ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return predictions


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Get prediction statistics."""
    total_preds = db.query(Prediction).count()
    
    bullish = db.query(Prediction).filter(Prediction.direction == "UP").count()
    bearish = db.query(Prediction).filter(Prediction.direction == "DOWN").count()
    
    buy_signals = db.query(Prediction).filter(Prediction.signal == "BUY").count()
    sell_signals = db.query(Prediction).filter(Prediction.signal == "SELL").count()
    
    avg_confidence = db.query(Prediction).all()
    avg_conf = sum(p.confidence for p in avg_confidence) / len(avg_confidence) if avg_confidence else 0
    
    return {
        "total_predictions": total_preds,
        "bullish": bullish,
        "bearish": bearish,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "average_confidence": round(avg_conf, 4)
    }
