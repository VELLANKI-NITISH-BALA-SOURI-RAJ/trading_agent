"""Quick system tests"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_imports():
    """Test all imports work"""
    try:
        from src.data_fetcher import CryptoDataFetcher
        from src.regime_detector import RegimeDetector
        from src.trading_agent import LangChainTradingAgent
        from src.config import config
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_fetch():
    """Test data fetching"""
    try:
        from src.data_fetcher import CryptoDataFetcher
        fetcher = CryptoDataFetcher()
        df = fetcher.get_ohlcv('BTC/USDT', '5m', limit=50)
        if df is not None and len(df) > 0:
            print(f"✅ Data fetch successful: {len(df)} candles")
            return True
        else:
            print("❌ No data returned")
            return False
    except Exception as e:
        print(f"❌ Data fetch error: {e}")
        return False

def test_regime_detection():
    """Test regime detection"""
    try:
        from src.data_fetcher import CryptoDataFetcher
        from src.regime_detector import RegimeDetector
        
        fetcher = CryptoDataFetcher()
        detector = RegimeDetector()
        
        df = fetcher.get_ohlcv('BTC/USDT', '5m', limit=100)
        df = fetcher.calculate_indicators(df)
        regime = detector.detect(df)
        
        if regime:
            print(f"✅ Regime detection successful: {regime['regime']}")
            return True
        else:
            print("❌ Regime detection failed")
            return False
    except Exception as e:
        print(f"❌ Regime detection error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running system tests...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Data Fetch", test_data_fetch),
        ("Regime Detection", test_regime_detection)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n Testing {name}...")
        results.append(test_func())
    
    print("\n" + "="*50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*50)