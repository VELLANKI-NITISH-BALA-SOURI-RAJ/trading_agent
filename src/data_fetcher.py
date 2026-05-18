import ccxt
import pandas as pd
import ta
from datetime import datetime
import time

class CryptoDataFetcher:
    """Fetch and process cryptocurrency market data"""
    
    def __init__(self, exchange_name='binance'):
        try:
            self.exchange = getattr(ccxt, exchange_name)({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        except Exception as e:
            print(f"Error initializing exchange: {e}")
            self.exchange = None
        
        try:
            self.wazirx_exchange = ccxt.wazirx({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        except Exception as e:
            print(f"Error initializing WazirX exchange: {e}")
            self.wazirx_exchange = None
    
    def get_ohlcv(self, symbol='BTC/USDT', timeframe='5m', limit=200):
        """Fetch OHLCV candlestick data"""
        retries = 3
        delay = 1.0
        exchange = self.wazirx_exchange if symbol.endswith('/INR') else self.exchange
        
        for attempt in range(retries):
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(
                    ohlcv, 
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
            except Exception as e:
                if "2136" in str(e) or "Too many api request" in str(e) or "RateLimitExceeded" in str(e) or "429" in str(e):
                    print(f"Rate limit hit for {symbol} on attempt {attempt+1}/{retries}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    print(f"Error fetching OHLCV for {symbol} on attempt {attempt+1}: {e}")
                    time.sleep(1.0)
        return None
    
    def calculate_indicators(self, df):
        """Calculate technical indicators for regime detection"""
        if df is None or len(df) < 50:
            return None
        
        df = df.copy()
        
        # Price-based indicators
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std() * 100
        
        # Moving averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # Trend indicator
        df['trend'] = (df['sma_20'] > df['sma_50']).astype(int)
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_surge'] = df['volume'] / df['volume_sma']
        
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['bb_high'] = bollinger.bollinger_hband()
        df['bb_low'] = bollinger.bollinger_lband()
        df['bb_mid'] = bollinger.bollinger_mavg()
        
        # ATR (Average True Range)
        df['atr'] = ta.volatility.AverageTrueRange(
            df['high'], df['low'], df['close']
        ).average_true_range()
        
        return df.dropna()
    
    def get_latest_price(self, symbol='BTC/USDT'):
        """Get latest ticker price"""
        retries = 3
        delay = 1.0
        exchange = self.wazirx_exchange if symbol.endswith('/INR') else self.exchange
        
        for attempt in range(retries):
            try:
                ticker = exchange.fetch_ticker(symbol)
                return {
                    'symbol': symbol,
                    'price': ticker.get('last', 0.0),
                    'volume_24h': ticker.get('quoteVolume', 0.0) if ticker.get('quoteVolume') is not None else 0.0,
                    'change_24h': ticker.get('percentage', 0.0) if ticker.get('percentage') is not None else 0.0
                }
            except Exception as e:
                if "2136" in str(e) or "Too many api request" in str(e) or "RateLimitExceeded" in str(e) or "429" in str(e):
                    print(f"Rate limit hit for {symbol} ticker on attempt {attempt+1}/{retries}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    print(f"Error fetching ticker for {symbol} on attempt {attempt+1}: {e}")
                    time.sleep(1.0)
        return None