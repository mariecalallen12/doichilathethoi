"""
Analysis Service
Digital Utopia Platform

Business logic cho Analysis operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
import logging

from ..models.market import MarketAnalysis, MarketDataHistory, MarketPrice

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service class cho Analysis operations
    
    Cung cấp business logic cho:
    - Technical analysis
    - Fundamental analysis
    - Market sentiment
    - Trading signals
    - Backtesting
    """
    
    def __init__(self, db: Session):
        """
        Khởi tạo AnalysisService
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    # =============== Technical Analysis ===============
    
    def get_technical_analysis(
        self,
        symbol: str,
        timeframe: str = "1d",
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Lấy technical analysis cho symbol
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w)
            indicators: List of indicators to include
            
        Returns:
            Dict với technical analysis data
        """
        # Get latest market analysis
        analysis = self.db.query(MarketAnalysis).filter(
            and_(
                MarketAnalysis.symbol == symbol.upper(),
                MarketAnalysis.analysis_type == "technical",
                MarketAnalysis.timeframe == timeframe
            )
        ).order_by(desc(MarketAnalysis.analysis_date)).first()
        
        if not analysis:
            # Return default structure if no analysis found
            return {
                "symbol": symbol.upper(),
                "timeframe": timeframe,
                "indicators": {},
                "signals": [],
                "price_prediction": {},
                "confidence_score": 0.0,
                "analysis_date": datetime.utcnow()
            }
        
        # Filter indicators if specified
        indicators_data = analysis.indicators or {}
        if indicators:
            indicators_data = {
                k: v for k, v in indicators_data.items()
                if k in indicators
            }
        
        return {
            "symbol": analysis.symbol,
            "timeframe": analysis.timeframe,
            "indicators": indicators_data,
            "signals": analysis.signals or [],
            "price_prediction": analysis.price_prediction or {},
            "confidence_score": float(analysis.confidence_score or 0.0),
            "analysis_date": analysis.analysis_date
        }
    
    # =============== Fundamental Analysis ===============
    
    def get_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Lấy fundamental analysis cho symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict với fundamental analysis data
        """
        # Get latest fundamental analysis
        analysis = self.db.query(MarketAnalysis).filter(
            and_(
                MarketAnalysis.symbol == symbol.upper(),
                MarketAnalysis.analysis_type == "fundamental"
            )
        ).order_by(desc(MarketAnalysis.analysis_date)).first()
        
        if not analysis:
            # Return default structure if no analysis found
            return {
                "symbol": symbol.upper(),
                "indicators": {},
                "signals": [],
                "confidence_score": 0.0,
                "analysis_date": datetime.utcnow()
            }
        
        return {
            "symbol": analysis.symbol,
            "indicators": analysis.indicators or {},
            "signals": analysis.signals or [],
            "confidence_score": float(analysis.confidence_score or 0.0),
            "analysis_date": analysis.analysis_date
        }
    
    # =============== Market Sentiment ===============
    
    def get_sentiment(
        self,
        symbol: Optional[str] = None,
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """
        Lấy market sentiment
        
        Args:
            symbol: Optional trading symbol
            timeframe: Timeframe for sentiment analysis
            
        Returns:
            Dict với sentiment data
        """
        query = self.db.query(MarketAnalysis).filter(
            MarketAnalysis.analysis_type == "sentiment"
        )
        
        if symbol:
            query = query.filter(MarketAnalysis.symbol == symbol.upper())
        
        analysis = query.order_by(desc(MarketAnalysis.analysis_date)).first()
        
        if not analysis:
            # Return default sentiment
            return {
                "symbol": symbol.upper() if symbol else None,
                "sentiment_score": 0.0,
                "bullish_percent": 50.0,
                "bearish_percent": 50.0,
                "neutral_percent": 0.0,
                "sources": {},
                "timestamp": datetime.utcnow()
            }
        
        sentiment_score = float(analysis.sentiment_score or 0.0)
        
        # Calculate percentages from sentiment score
        if sentiment_score > 0:
            bullish_percent = min(100.0, 50.0 + sentiment_score / 2)
            bearish_percent = 100.0 - bullish_percent
            neutral_percent = 0.0
        elif sentiment_score < 0:
            bearish_percent = min(100.0, 50.0 + abs(sentiment_score) / 2)
            bullish_percent = 100.0 - bearish_percent
            neutral_percent = 0.0
        else:
            bullish_percent = 33.33
            bearish_percent = 33.33
            neutral_percent = 33.34
        
        return {
            "symbol": analysis.symbol if symbol else None,
            "sentiment_score": sentiment_score,
            "bullish_percent": bullish_percent,
            "bearish_percent": bearish_percent,
            "neutral_percent": neutral_percent,
            "sources": analysis.meta_data or {},
            "timestamp": analysis.analysis_date
        }
    
    # =============== Trading Signals ===============
    
    def get_signals(
        self,
        symbol: Optional[str] = None,
        timeframe: str = "1d",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Lấy trading signals
        
        Args:
            symbol: Optional trading symbol
            timeframe: Timeframe
            limit: Number of signals to return
            
        Returns:
            List of trading signals
        """
        query = self.db.query(MarketAnalysis).filter(
            and_(
                MarketAnalysis.analysis_type.in_(["technical", "fundamental"]),
                MarketAnalysis.timeframe == timeframe
            )
        )
        
        if symbol:
            query = query.filter(MarketAnalysis.symbol == symbol.upper())
        
        analyses = query.order_by(desc(MarketAnalysis.analysis_date)).limit(limit).all()
        
        signals = []
        for analysis in analyses:
            signals_list = analysis.signals or []
            for signal in signals_list:
                if isinstance(signal, dict):
                    signals.append({
                        "symbol": analysis.symbol,
                        "signal_type": signal.get("type", "hold"),
                        "strength": float(signal.get("strength", 0.5)),
                        "price_target": signal.get("price_target"),
                        "stop_loss": signal.get("stop_loss"),
                        "timeframe": analysis.timeframe,
                        "indicators": analysis.indicators or {},
                        "confidence": float(analysis.confidence_score or 0.0) / 100.0,
                        "timestamp": analysis.analysis_date
                    })
        
        return signals[:limit]
    
    # =============== Backtest ===============
    
    def run_backtest(
        self,
        symbol: str,
        strategy: str,
        start_date: datetime,
        end_date: datetime,
        initial_balance: float = 10000.0,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chạy backtest cho trading strategy
        
        Args:
            symbol: Trading symbol
            strategy: Strategy name or ID
            start_date: Backtest start date
            end_date: Backtest end date
            initial_balance: Initial balance
            parameters: Strategy parameters
            
        Returns:
            Dict với backtest results
        """
        # Get historical data
        historical_data = self.db.query(MarketDataHistory).filter(
            and_(
                MarketDataHistory.symbol == symbol.upper(),
                MarketDataHistory.timestamp >= start_date,
                MarketDataHistory.timestamp <= end_date
            )
        ).order_by(MarketDataHistory.timestamp.asc()).all()
        
        if not historical_data:
            raise ValueError(f"No historical data found for {symbol} in the specified date range")
        
        # Simple backtest simulation
        # In production, this would use actual strategy logic
        balance = initial_balance
        trades = []
        equity_curve = []
        winning_trades = 0
        losing_trades = 0
        total_win = 0.0
        total_loss = 0.0
        
        # Simulate trades (simplified)
        for i, data in enumerate(historical_data[1:], 1):
            prev_data = historical_data[i - 1]
            
            # Simple strategy: buy if price increased, sell if decreased
            if float(data.close_price) > float(prev_data.close_price):
                # Buy signal
                trade_amount = balance * 0.1  # Use 10% of balance
                entry_price = float(data.close_price)
                
                # Find exit (simplified)
                if i + 1 < len(historical_data):
                    exit_price = float(historical_data[i + 1].close_price)
                    pnl = (exit_price - entry_price) / entry_price * trade_amount
                    balance += pnl
                    
                    trade = {
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl": pnl,
                        "timestamp": data.timestamp
                    }
                    trades.append(trade)
                    
                    if pnl > 0:
                        winning_trades += 1
                        total_win += pnl
                    else:
                        losing_trades += 1
                        total_loss += abs(pnl)
            
            equity_curve.append({
                "timestamp": data.timestamp,
                "balance": balance
            })
        
        final_balance = balance
        total_return = final_balance - initial_balance
        total_return_percent = (total_return / initial_balance) * 100.0
        
        # Calculate max drawdown
        max_balance = initial_balance
        max_drawdown = 0.0
        for point in equity_curve:
            if point["balance"] > max_balance:
                max_balance = point["balance"]
            drawdown = (max_balance - point["balance"]) / max_balance * 100.0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        win_rate = (winning_trades / len(trades) * 100.0) if trades else 0.0
        average_win = total_win / winning_trades if winning_trades > 0 else 0.0
        average_loss = total_loss / losing_trades if losing_trades > 0 else 0.0
        profit_factor = total_win / total_loss if total_loss > 0 else 0.0
        
        return {
            "backtest_id": f"bt_{symbol}_{int(datetime.utcnow().timestamp())}",
            "symbol": symbol.upper(),
            "strategy": strategy,
            "start_date": start_date,
            "end_date": end_date,
            "initial_balance": initial_balance,
            "final_balance": final_balance,
            "total_return": total_return,
            "total_return_percent": total_return_percent,
            "max_drawdown": max_drawdown,
            "max_drawdown_percent": max_drawdown,
            "sharpe_ratio": None,  # Would need to calculate
            "total_trades": len(trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "average_win": average_win,
            "average_loss": average_loss,
            "profit_factor": profit_factor,
            "trades": trades[:100],  # Limit to 100 trades
            "equity_curve": equity_curve[-100:],  # Last 100 points
            "metadata": {
                "parameters": parameters or {},
                "created_at": datetime.utcnow()
            }
        }

