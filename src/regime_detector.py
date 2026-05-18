import pandas as pd
from src.config import config

class RegimeDetector:
    """Detect market regimes using technical indicators"""
    
    def __init__(self):
        self.regimes = {
            'BULL_TRENDING': {
                'description': 'Strong upward momentum with healthy volume',
                'base_risk': 4
            },
            'BEAR_TRENDING': {
                'description': 'Strong downward momentum, high selling pressure',
                'base_risk': 6
            },
            'HIGH_VOLATILITY': {
                'description': 'Extreme price swings, unpredictable movement',
                'base_risk': 9
            },
            'VOLUME_SPIKE': {
                'description': 'Unusual volume activity, potential breakout',
                'base_risk': 7
            },
            'SIDEWAYS': {
                'description': 'Range-bound, no clear trend',
                'base_risk': 3
            },
            'OVERSOLD': {
                'description': 'Potential reversal upward, RSI indicates oversold',
                'base_risk': 5
            },
            'OVERBOUGHT': {
                'description': 'Potential reversal downward, RSI indicates overbought',
                'base_risk': 5
            }
        }
    
    def detect(self, df):
        """Detect current market regime"""
        if df is None or len(df) == 0:
            return None
        
        latest = df.iloc[-1]
        
        # Extract key metrics
        volatility = latest['volatility']
        trend = latest['trend']
        volume_surge = latest['volume_surge']
        rsi = latest['rsi']
        macd_diff = latest['macd_diff']
        
        # Calculate price changes
        price_change_1h = (df['close'].iloc[-12:].pct_change().sum()) * 100
        price_change_4h = (df['close'].iloc[-48:].pct_change().sum()) * 100
        
        # Regime detection logic
        regime = None
        
        # High volatility check (priority)
        if volatility > config.HIGH_VOLATILITY_THRESHOLD:
            regime = 'HIGH_VOLATILITY'
        
        # RSI extremes
        elif rsi < 30:
            regime = 'OVERSOLD'
        elif rsi > 70:
            regime = 'OVERBOUGHT'
        
        # Volume spike
        elif volume_surge > config.VOLUME_SURGE_THRESHOLD:
            regime = 'VOLUME_SPIKE'
        
        # Trending markets
        elif trend == 1 and price_change_1h > config.TREND_CHANGE_THRESHOLD and macd_diff > 0:
            regime = 'BULL_TRENDING'
        elif trend == 0 and price_change_1h < -config.TREND_CHANGE_THRESHOLD and macd_diff < 0:
            regime = 'BEAR_TRENDING'
        
        # Default to sideways
        else:
            regime = 'SIDEWAYS'
        
        # Compile regime data
        regime_info = self.regimes[regime]
        
        return {
            'regime': regime,
            'description': regime_info['description'],
            'risk_level': regime_info['base_risk'],
            'confidence': self._calculate_confidence(df, regime),
            'metrics': {
                'volatility': round(volatility, 2),
                'trend_direction': 'Bullish' if trend == 1 else 'Bearish',
                'price_change_1h': round(price_change_1h, 2),
                'price_change_4h': round(price_change_4h, 2),
                'volume_surge': round(volume_surge, 2),
                'rsi': round(rsi, 2),
                'macd_diff': round(macd_diff, 4),
                'current_price': round(latest['close'], 2)
            }
        }
    
    def _calculate_confidence(self, df, regime):
        """Calculate confidence score for regime detection (0-100)"""
        # Simple confidence based on consistency
        latest = df.iloc[-1]
        
        if regime == 'HIGH_VOLATILITY':
            # Higher volatility = higher confidence in this regime
            return min(100, int(latest['volatility'] * 20))
        
        elif regime in ['BULL_TRENDING', 'BEAR_TRENDING']:
            # Trend consistency over last 10 candles
            recent_trends = df['trend'].iloc[-10:]
            consistency = (recent_trends.sum() / 10) * 100
            return int(consistency if regime == 'BULL_TRENDING' else 100 - consistency)
        
        elif regime in ['OVERSOLD', 'OVERBOUGHT']:
            # Distance from extreme
            rsi = latest['rsi']
            if regime == 'OVERSOLD':
                return int((30 - rsi) * 3.33) if rsi < 30 else 0
            else:
                return int((rsi - 70) * 3.33) if rsi > 70 else 0
        
        else:
            return 70  # Default confidence