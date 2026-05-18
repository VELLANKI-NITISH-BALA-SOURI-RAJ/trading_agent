import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Trading pairs
    SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BTC/INR', 'ETH/INR', 'SOL/INR', 'USDT/INR']
    
    # Data settings
    TIMEFRAME = '5m'
    CANDLES_LIMIT = 200
    
    # Regime thresholds
    HIGH_VOLATILITY_THRESHOLD = 2.5
    VOLUME_SURGE_THRESHOLD = 2.0
    TREND_CHANGE_THRESHOLD = 1.0
    
    # Risk settings
    MAX_POSITION_SIZE = 30  # percentage
    DEFAULT_STOP_LOSS = 2.5  # percentage

config = Config()