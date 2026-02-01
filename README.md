# Stock Prediction API

A FastAPI-based backend for stock price direction prediction using XGBoost machine learning model.

## Features

- **ML-based Predictions**: 5-day stock price direction forecasting using XGBoost
- **User Management**: Registration, login, and authentication with JWT
- **Watchlists**: Create and manage custom watchlists
- **Prediction History**: Store and retrieve past predictions
- **Live Market Data**: Integration with yfinance for real-time data
- **Batch Predictions**: Get predictions for multiple symbols at once
- **Statistics**: Track prediction accuracy and signal performance
- **REST API**: Full FastAPI with Swagger documentation

## Installation

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Set environment variables** (create `.env` file):
```
SECRET_KEY=your-secret-key-here
DEBUG=false
DATABASE_URL=sqlite:///./stock_pred.db
```

3. **Run the server**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### Predictions
- `POST /api/predict/` - Get prediction for a symbol
- `POST /api/predict/batch` - Get predictions for multiple symbols
- `GET /api/predict/history/{symbol}` - Get recent predictions for a symbol

### Users
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login and get token
- `GET /api/users/me` - Get current user

### Watchlists
- `POST /api/watchlists/` - Create watchlist
- `GET /api/watchlists/{watchlist_id}` - Get watchlist
- `POST /api/watchlists/{watchlist_id}/symbols` - Add symbol
- `DELETE /api/watchlists/{watchlist_id}/symbols/{symbol}` - Remove symbol

### History & Statistics
- `GET /api/history/predictions` - Get prediction history
- `GET /api/history/predictions/{symbol}` - Get symbol history
- `GET /api/history/statistics` - Get overall statistics

## Model Details

The XGBoost model predicts 5-day stock price direction using:
- Price returns (1-day, 5-day)
- Moving averages (10-day, 20-day)
- Exponential moving average (10-day)
- Volatility (10-day rolling std)
- Lag features (1-day, 5-day prices)

**Prediction Signals**:
- **BUY**: Confidence > 55% (strong uptrend)
- **SELL**: Confidence < 45% (strong downtrend)
- **NO_TRADE**: 45% ≤ Confidence ≤ 55% (uncertain)

## Database

Uses SQLite for simplicity. To use PostgreSQL:
```
DATABASE_URL=postgresql://user:password@localhost/stock_pred
pip install psycopg2-binary
```

## Testing

Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

**Get a prediction**:
```bash
curl -X POST "http://localhost:8000/api/predict/" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

**Response**:
```json
{
  "symbol": "AAPL",
  "direction": "UP",
  "confidence": 0.6234,
  "signal": "BUY",
  "timestamp": "2025-01-31T10:30:00"
}
```

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Ensemble model predictions
- [ ] Portfolio backtesting endpoint
- [ ] Alert system for signals
- [ ] Performance metrics dashboard
- [ ] Data caching layer (Redis)
- [ ] Rate limiting and quotas
- [ ] Email notifications
- [ ] Mobile app integration
