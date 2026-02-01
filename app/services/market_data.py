import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime, timedelta
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MarketDataService:
    """Fetch live market data using yfinance with fallback to mock data."""
    
    def __init__(self):
        self._cache = {}
        self._cache_duration = timedelta(minutes=5)
        
        # Create a robust session with retries and proper headers
        self._session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        
        # Set comprehensive headers to avoid blocking
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Set longer timeout
        self._timeout = 30
    
    def _get_from_cache(self, key: str) -> Optional[any]:
        """Get data from cache if not expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_duration:
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: any):
        """Store data in cache with timestamp."""
        self._cache[key] = (data, datetime.now())
    
    def _generate_mock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """Generate realistic mock stock data for testing."""
        print(f"📊 Generating mock data for {symbol} (Yahoo Finance unavailable)")
        
        # Determine number of days based on period
        days_map = {"1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "1y": 365}
        days = days_map.get(period, 90)
        
        # Generate dates
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate realistic stock prices with trend and volatility
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        # Starting price based on symbol hash (realistic range)
        start_price = 50 + (hash(symbol) % 450)
        
        # Generate price movements
        returns = np.random.normal(0.0005, 0.02, days)  # Small daily returns with volatility
        prices = start_price * (1 + returns).cumprod()
        
        # Create OHLCV data
        df = pd.DataFrame({
            'Open': prices * np.random.uniform(0.98, 1.02, days),
            'High': prices * np.random.uniform(1.00, 1.05, days),
            'Low': prices * np.random.uniform(0.95, 1.00, days),
            'Close': prices,
            'Volume': np.random.randint(1_000_000, 100_000_000, days)
        }, index=dates)
        
        # Ensure High is highest and Low is lowest
        df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
        df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
        
        return df
    
    def get_historical_data(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for a symbol with fallback to mock data.
        
        Args:
            symbol: Stock ticker (e.g., "AAPL")
            period: Data period ("1mo", "3mo", "1y", etc.)
        
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"hist_{symbol}_{period}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            print(f"💾 Using cached data for {symbol}")
            return cached
        
        # Method 1: Try ticker.history() with session
        try:
            print(f"🔍 Fetching real data for {symbol} (Method 1: ticker.history)...")
            time.sleep(1.5)  # Rate limiting delay
            
            ticker = yf.Ticker(symbol, session=self._session)
            df = ticker.history(period=period, timeout=self._timeout, threads=False)
            
            if not df.empty:
                required_cols = ["Open", "High", "Low", "Close", "Volume"]
                if all(col in df.columns for col in required_cols):
                    result = df[required_cols]
                    self._set_cache(cache_key, result)
                    print(f"✅ Successfully fetched real data for {symbol}")
                    return result
        except Exception as e:
            print(f"❌ Method 1 failed: {str(e)[:100]}")
        
        # Method 2: Try download() method with threads=False
        try:
            print(f"🔍 Fetching real data for {symbol} (Method 2: yf.download)...")
            time.sleep(1.5)  # Rate limiting delay
            
            df = yf.download(
                symbol, 
                period=period, 
                progress=False,
                timeout=self._timeout,
                ignore_tz=True,
                threads=False  # Disable multi-threading to avoid rate limits
            )
            
            if not df.empty:
                required_cols = ["Open", "High", "Low", "Close", "Volume"]
                if all(col in df.columns for col in required_cols):
                    result = df[required_cols]
                    self._set_cache(cache_key, result)
                    print(f"✅ Successfully fetched real data for {symbol}")
                    return result
        except Exception as e:
            print(f"❌ Method 2 failed: {str(e)[:100]}")
        
        # Fallback to mock data
        print(f"⚠️  All methods failed, using mock data for {symbol}")
        mock_data = self._generate_mock_data(symbol, period)
        self._set_cache(cache_key, mock_data)
        return mock_data
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest closing price for a symbol."""
        cache_key = f"price_{symbol}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = self.get_historical_data(symbol, period="1d")
            if df is not None and not df.empty:
                price = float(df['Close'].iloc[-1])
                self._set_cache(cache_key, price)
                return price
            return None
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol exists (always returns True with mock fallback)."""
        cache_key = f"valid_{symbol}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Accept common stock symbols (basic validation)
        if symbol and len(symbol) >= 1 and len(symbol) <= 5 and symbol.isalpha():
            self._set_cache(cache_key, True)
            return True
        
        return False


market_data_service = MarketDataService()
