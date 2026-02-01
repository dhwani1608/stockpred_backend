from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.prediction import Prediction
from app.services.ml_service import ml_service
from app.services.market_data import market_data_service
from app.utils.features import calculate_features
from typing import Optional
from datetime import datetime
import time

router = APIRouter(prefix="/api/predict", tags=["predictions"])


class PredictionInput(BaseModel):
    symbol: str
    use_live_data: bool = True


class BatchPredictionInput(BaseModel):
    symbols: list[str]


class PredictionResponse(BaseModel):
    symbol: str
    direction: str
    confidence: float
    signal: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=PredictionResponse)
def predict(
    input_data: PredictionInput,
    db: Session = Depends(get_db)
) -> PredictionResponse:
    """
    Make a prediction for a stock symbol.
    
    If use_live_data=True, fetches latest data from yfinance.
    Otherwise, requires manual feature input.
    """
    symbol = input_data.symbol.upper()
    
    try:
        # Validate symbol
        if not market_data_service.validate_symbol(symbol):
            raise HTTPException(status_code=400, detail=f"Invalid symbol: {symbol}")
        
        # Fetch historical data
        hist_data = market_data_service.get_historical_data(symbol, period="3mo")
        if hist_data is None or len(hist_data) < 20:
            raise HTTPException(status_code=400, detail=f"Insufficient data for {symbol}")
    except HTTPException:
        raise
    except Exception as e:
        # Handle rate limiting or network errors
        error_msg = str(e)
        if "429" in error_msg or "Too Many Requests" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again in a few moments. Data is cached for 5 minutes."
            )
        raise HTTPException(status_code=500, detail=f"Error fetching data: {error_msg}")
    
    # Calculate features
    features = calculate_features(hist_data)
    
    # Make prediction
    direction, confidence, signal = ml_service.predict(features)
    
    # Store in database
    pred = Prediction(
        symbol=symbol,
        direction=direction,
        confidence=confidence,
        signal=signal,
        close_price=features["Close"],
        return_1=features["Return_1"],
        return_5=features["Return_5"],
        ma_10=features["MA_10"],
        ma_20=features["MA_20"],
        ema_10=features["EMA_10"],
        volatility_10=features["Volatility_10"],
        lag_1=features["Lag_1"],
        lag_5=features["Lag_5"],
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    
    return {
        "symbol": symbol,
        "direction": direction,
        "confidence": round(confidence, 4),
        "signal": signal,
        "timestamp": datetime.now()
    }


@router.post("/batch")
def predict_batch(input_data: BatchPredictionInput, db: Session = Depends(get_db)):
    """Make predictions for multiple symbols."""
    results = []
    for idx, symbol in enumerate(input_data.symbols):
        try:
            # Add delay between batch requests (1-2 seconds)
            if idx > 0:  # Don't sleep before first request
                time.sleep(1.5)
            
            result = predict(PredictionInput(symbol=symbol), db)
            results.append(result)
        except HTTPException as e:
            results.append({"symbol": symbol, "error": e.detail})
    return results


@router.get("/history/{symbol}")
def get_prediction_history(symbol: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get recent predictions for a symbol."""
    predictions = db.query(Prediction).filter(
        Prediction.symbol == symbol.upper()
    ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return predictions
