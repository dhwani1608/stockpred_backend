from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
import numpy as np
import joblib

# =========================
# LOAD MODEL
# =========================
model = joblib.load("model/xgboost_5day_direction.pkl")

FEATURES = [
    "Close",
    "Return_1",
    "Return_5",
    "MA_10",
    "MA_20",
    "EMA_10",
    "Volatility_10",
    "Lag_1",
    "Lag_5"
]

app = FastAPI(
    title="Live Stock Prediction API",
    description="Predicts 5-day stock direction (single & batch)",
    version="1.1"
)

# =========================
# REQUEST SCHEMA (BATCH)
# =========================
class BatchRequest(BaseModel):
    symbols: list[str]

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def health():
    return {"status": "API is running"}

# =========================
# FEATURE ENGINEERING
# =========================
def compute_features(df: pd.DataFrame):
    df = df.copy()

    df["Return_1"] = df["Close"].pct_change()
    df["Return_5"] = df["Close"].pct_change(5)
    df["MA_10"] = df["Close"].rolling(10).mean()
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["EMA_10"] = df["Close"].ewm(span=10).mean()
    df["Volatility_10"] = df["Return_1"].rolling(10).std()
    df["Lag_1"] = df["Close"].shift(1)
    df["Lag_5"] = df["Close"].shift(5)

    df = df.dropna()
    return df.iloc[-1][FEATURES].values.reshape(1, -1)

# =========================
# BATCH PREDICTION (MUST BE FIRST)
# =========================
@app.post("/predict/batch")
def predict_batch(request: BatchRequest):
    results = []

    for symbol in request.symbols:
        try:
            result = _predict_one(symbol)
            results.append(result)
        except Exception as e:
            results.append({
                "symbol": symbol.upper(),
                "error": str(e)
            })

    return {"results": results}


# =========================
# SINGLE STOCK PREDICTION
# =========================
@app.post("/predict/{symbol}")
def predict_stock(symbol: str):
    return _predict_one(symbol)

# =========================
# CORE PREDICTION LOGIC
# =========================
def _predict_one(symbol: str):
    df = yf.download(
        symbol,
        period="3mo",
        interval="1d",
        progress=False
    )

    if df.empty or len(df) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for {symbol}"
        )

    X = compute_features(df)
    proba_up = model.predict_proba(X)[0][1]

    if proba_up > 0.55:
        signal = "BUY"
    elif proba_up < 0.45:
        signal = "SELL"
    else:
        signal = "NO_TRADE"

    return {
        "symbol": symbol.upper(),
        "prediction": "UP" if proba_up > 0.5 else "DOWN",
        "confidence": round(float(proba_up), 4),
        "signal": signal
    }