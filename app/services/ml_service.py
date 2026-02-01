import joblib
import numpy as np
from typing import Dict, Tuple
from app.config import settings


class MLService:
    def __init__(self):
        self.model = joblib.load(settings.MODEL_PATH)
        self.feature_names = [
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
    
    def predict(self, features: Dict[str, float]) -> Tuple[str, float, str]:
        """
        Make prediction using the trained XGBoost model.
        
        Returns: (direction, confidence, signal)
        """
        # Build feature vector in correct order
        X = np.array([[features[f] for f in self.feature_names]])
        
        # Get probability of UP move
        proba_up = float(self.model.predict_proba(X)[0][1])
        
        # Direction
        direction = "UP" if proba_up > 0.5 else "DOWN"
        
        # Trading signal with confidence filter
        if proba_up > 0.55:
            signal = "BUY"
        elif proba_up < 0.45:
            signal = "SELL"
        else:
            signal = "NO_TRADE"
        
        return direction, proba_up, signal


# Singleton instance
ml_service = MLService()
