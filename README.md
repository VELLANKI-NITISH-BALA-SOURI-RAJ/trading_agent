# 🤖 Autonomous Trading Agent

An AI-powered cryptocurrency trading system built with LangChain, featuring multi-agent analysis and regime-based decision making.

## 🎯 Features

- **Real-time Market Data**: Live crypto data from Binance via CCXT
- **Regime Detection**: Intelligent market state classification (Bull/Bear/Sideways/High Volatility)
- **Multi-Agent System**: Specialized LangChain agents for analysis, risk management, and signal generation
- **Technical Analysis**: 15+ indicators including RSI, MACD, Bollinger Bands, ATR
- **Risk Management**: Dynamic position sizing based on regime and confidence
- **Interactive Dashboard**: Beautiful Streamlit interface with live charts

## 🏗️ Architecture
Market Data → Regime Detection → LangChain Agents → Trading Signal
↓              ↓                    ↓               ↓
CCXT      Rule Engine         GPT-4o-mini      BUY/SELL/HOLD
## 🚀 Quick Start

See SETUP_STEPS.md for detailed instructions.

## 📊 Regime Types

| Regime | Description | Risk Level |
|--------|-------------|------------|
| BULL_TRENDING | Strong upward momentum | 4/10 |
| BEAR_TRENDING | Strong downward pressure | 6/10 |
| HIGH_VOLATILITY | Extreme price swings | 9/10 |
| SIDEWAYS | Range-bound market | 3/10 |
| OVERSOLD | Potential bounce | 5/10 |
| OVERBOUGHT | Potential correction | 5/10 |

## 🛠️ Tech Stack

- **AI Framework**: LangChain + OpenAI GPT-4o-mini
- **Data**: CCXT (Binance API)
- **Analysis**: Pandas, TA-Lib indicators
- **Dashboard**: Streamlit + Plotly
- **Language**: Python 3.9+

## 📈 Performance

Built for overnight demo - optimized for:
- Fast prototyping
- Clear decision explanations
- Production-ready architecture
- Extensible design for RL/backtesting

## 🎓 Learning Goals

This project demonstrates:
- Multi-agent AI systems
- Financial market analysis
- Real-time data processing
- Risk management
- Production-grade code structure

## 📝 License

MIT License - Built for CoinDCX Internship Application

## 👤 Author

Built in one night to showcase AI + Trading expertise 🚀