from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import config
import json

# Define custom tools for the agent
@tool
def analyze_regime(regime_data: str) -> str:
    """
    Analyzes the current market regime and returns key insights.
    Input should be a JSON string with regime information.
    """
    try:
        data = json.loads(regime_data)
        regime = data.get('regime', 'UNKNOWN')
        risk = data.get('risk_level', 5)
        
        analysis = f"""
        Market Regime Analysis:
        - Current State: {regime}
        - Risk Level: {risk}/10
        - Confidence: {data.get('confidence', 0)}%
        
        Key Metrics:
        - Volatility: {data.get('metrics', {}).get('volatility', 'N/A')}%
        - RSI: {data.get('metrics', {}).get('rsi', 'N/A')}
        - 1H Price Change: {data.get('metrics', {}).get('price_change_1h', 'N/A')}%
        """
        
        return analysis
    except Exception as e:
        return f"Error analyzing regime: {str(e)}"

@tool
def calculate_position_size(risk_level: int, confidence: int) -> str:
    """
    Calculates optimal position size based on risk level and confidence.
    risk_level: 1-10 (higher = more risky)
    confidence: 0-100 (higher = more confident in signal)
    """
    # Risk-adjusted position sizing
    base_size = config.MAX_POSITION_SIZE
    
    # Reduce size for high risk
    risk_adjustment = 1 - (risk_level / 20)  # 0.5 to 0.95
    
    # Increase size for high confidence
    confidence_adjustment = confidence / 100  # 0 to 1
    
    position_size = base_size * risk_adjustment * confidence_adjustment
    position_size = max(5, min(position_size, config.MAX_POSITION_SIZE))
    
    # Calculate stop loss
    stop_loss = config.DEFAULT_STOP_LOSS * (1 + risk_level / 10)
    
    result = {
        "position_size_percent": round(position_size, 1),
        "stop_loss_percent": round(stop_loss, 2),
        "take_profit_percent": round(stop_loss * 2.5, 2),  # 2.5:1 reward/risk
        "risk_reward_ratio": "2.5:1"
    }
    
    return json.dumps(result)

@tool
def check_entry_conditions(regime: str, rsi: float, macd_diff: float) -> str:
    """
    Checks if current market conditions are favorable for entry.
    Returns a recommendation: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    """
    score = 0
    reasoning = []
    
    # Regime-based scoring
    if regime == 'BULL_TRENDING':
        score += 3
        reasoning.append("Strong bullish trend detected")
    elif regime == 'OVERSOLD':
        score += 2
        reasoning.append("Market oversold, potential bounce")
    elif regime == 'BEAR_TRENDING':
        score -= 3
        reasoning.append("Strong bearish trend, avoid longs")
    elif regime == 'OVERBOUGHT':
        score -= 2
        reasoning.append("Market overbought, correction risk")
    elif regime == 'HIGH_VOLATILITY':
        score -= 1
        reasoning.append("High volatility, increased risk")
    
    # RSI scoring
    if rsi < 30:
        score += 2
        reasoning.append(f"RSI={rsi:.1f} indicates oversold")
    elif rsi > 70:
        score -= 2
        reasoning.append(f"RSI={rsi:.1f} indicates overbought")
    elif 40 < rsi < 60:
        score += 1
        reasoning.append("RSI in neutral zone")
    
    # MACD scoring
    if macd_diff > 0:
        score += 1
        reasoning.append("MACD shows bullish momentum")
    elif macd_diff < 0:
        score -= 1
        reasoning.append("MACD shows bearish momentum")
    
    # Determine recommendation
    if score >= 4:
        recommendation = "STRONG_BUY"
    elif score >= 2:
        recommendation = "BUY"
    elif score <= -4:
        recommendation = "STRONG_SELL"
    elif score <= -2:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
    
    result = {
        "recommendation": recommendation,
        "score": score,
        "reasoning": reasoning
    }
    
    return json.dumps(result)


class LangChainTradingAgent:
    """Multi-agent trading system using LangChain"""
    
    def __init__(self):
        # Determine model and base URL dynamically based on the API key type
        api_key = config.OPENAI_API_KEY
        is_openrouter = api_key and api_key.startswith("sk-or-")
        
        model_name = "openai/gpt-4o-mini" if is_openrouter else "gpt-4o-mini"
        base_url = "https://openrouter.ai/api/v1" if is_openrouter else None
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.2,  # Low temperature for consistent trading decisions
            api_key=api_key,
            base_url=base_url
        )
        
        # Define tools
        self.tools = [
            analyze_regime,
            calculate_position_size,
            check_entry_conditions
        ]
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _get_system_prompt(self):
        return """You are an expert cryptocurrency trading agent specializing in regime-based trading strategies.

Your role is to:
1. Analyze market regimes and conditions
2. Assess risk levels and confidence
3. Generate clear, actionable trading signals
4. Provide risk management parameters

ALWAYS structure your final response in this exact format:

═══════════════════════════════════
🎯 TRADING SIGNAL
═══════════════════════════════════

SIGNAL: [STRONG_BUY | BUY | HOLD | SELL | STRONG_SELL]
CONFIDENCE: [1-10]/10

📊 POSITION MANAGEMENT
- Entry Size: [X]% of capital
- Stop Loss: [X]% from entry
- Take Profit: [X]% from entry
- Risk/Reward: [X:1]

💡 REASONING
[2-3 sentences explaining the key factors behind this decision]

⚠️ KEY RISKS
[1-2 main risks to watch]

═══════════════════════════════════

Use the available tools to analyze regime, calculate position sizing, and check entry conditions.
Be decisive but cautious. In uncertain conditions, prefer HOLD over risky trades."""
    
    def generate_signal(self, regime_data, price_data):
        """
        Generate trading signal based on regime and price data
        """
        try:
            # Prepare input for the agent
            metrics = regime_data['metrics']
            
            input_text = f"""
Analyze the following market data and provide a trading signal:

MARKET REGIME:
- Regime: {regime_data['regime']}
- Description: {regime_data['description']}
- Risk Level: {regime_data['risk_level']}/10
- Confidence: {regime_data['confidence']}%

CURRENT METRICS:
- Price: ${metrics['current_price']}
- Volatility: {metrics['volatility']}%
- RSI: {metrics['rsi']}
- MACD Diff: {metrics['macd_diff']}
- 1H Change: {metrics['price_change_1h']}%
- 4H Change: {metrics['price_change_4h']}%
- Volume Surge: {metrics['volume_surge']}x
- Trend: {metrics['trend_direction']}

Use your tools to analyze this data and generate a comprehensive trading signal.
"""
            
            # Execute agent
            response = self.agent_executor.invoke({
                "input": input_text
            })
            
            return response['output']
            
        except Exception as e:
            return f"Error generating signal: {str(e)}\n\nPlease check your OpenAI API key and try again."
    
    def quick_analysis(self, regime_data):
        """
        Generate a quick market analysis without full signal generation
        """
        try:
            input_text = f"""
Provide a brief 2-3 sentence market analysis for:

Regime: {regime_data['regime']}
Risk Level: {regime_data['risk_level']}/10
RSI: {regime_data['metrics']['rsi']}
Price Change (1H): {regime_data['metrics']['price_change_1h']}%

Keep it concise and actionable.
"""
            
            response = self.agent_executor.invoke({
                "input": input_text
            })
            
            return response['output']
            
        except Exception as e:
            return f"Error in analysis: {str(e)}"