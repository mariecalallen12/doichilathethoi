"""
Win Rate Controller Service
Service to control and adjust user win rates
"""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)


class WinRateController:
    """Service to control user win rate"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def adjust_user_win_rate(
        self,
        user_id: int,
        target_win_rate: float,
        admin_user_id: Optional[int] = None,
        mode: str = "gradual",
        timeframe_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Adjust user's win rate to target
        
        Args:
            user_id: User ID to adjust
            target_win_rate: Target win rate (0-100)
            admin_user_id: Admin performing the adjustment
            mode: "gradual" or "immediate"
            timeframe_hours: Timeframe for gradual adjustment
        
        Returns:
            Adjustment result summary
        """
        from ..models.portfolio import PortfolioPosition
        from ..models.system import TradingAdjustment
        
        try:
            # Validate target_win_rate
            if not 0 <= target_win_rate <= 100:
                raise ValueError("Target win rate must be between 0 and 100")
            
            # Get user's current open positions
            positions = self.db.query(PortfolioPosition).filter(
                PortfolioPosition.user_id == user_id,
                PortfolioPosition.status == "open"
            ).all()
            
            if not positions:
                logger.warning(f"No open positions for user {user_id}")
                return {
                    "user_id": user_id,
                    "previous_win_rate": self._calculate_win_rate(user_id),
                    "target_win_rate": target_win_rate,
                    "positions_adjusted": 0,
                    "mode": mode,
                    "message": "No open positions to adjust"
                }
            
            # Calculate current win rate
            current_win_rate = self._calculate_win_rate(user_id)
            needed_change = target_win_rate - current_win_rate
            
            logger.info(
                f"Adjusting win rate for user {user_id}: "
                f"current={current_win_rate:.1f}%, target={target_win_rate:.1f}%, "
                f"mode={mode}"
            )
            
            adjusted_positions = []
            
            if mode == "immediate":
                # Adjust positions immediately to reach target
                positions_to_win = int(len(positions) * (target_win_rate / 100))
                positions_to_lose = len(positions) - positions_to_win
                
                # Sort positions by P&L
                positions_sorted = sorted(positions, key=lambda p: p.unrealized_pnl or 0)
                
                # Make bottom positions winning
                for i, position in enumerate(positions_sorted[:positions_to_win]):
                    if position.unrealized_pnl is None or position.unrealized_pnl <= 0:
                        # Make profitable
                        position.unrealized_pnl = abs(float(position.quantity) * 0.02)  # 2% gain
                        adjusted_positions.append(position.id)
                
                # Make top positions losing  
                for i, position in enumerate(positions_sorted[positions_to_win:]):
                    if position.unrealized_pnl is None or position.unrealized_pnl >= 0:
                        # Make loss
                        position.unrealized_pnl = -abs(float(position.quantity) * 0.02)  # 2% loss
                        adjusted_positions.append(position.id)
                
                self.db.commit()
                
            elif mode == "gradual":
                # Plan gradual adjustments
                # For now, implement similar to immediate but with smaller changes
                for position in positions:
                    if needed_change > 0:
                        # Need more wins - adjust slightly positive
                        if position.unrealized_pnl is None or position.unrealized_pnl < 0:
                            current_pnl = position.unrealized_pnl or 0
                            position.unrealized_pnl = current_pnl + abs(float(position.quantity) * 0.01)
                            adjusted_positions.append(position.id)
                    else:
                        # Need more losses - adjust slightly negative  
                        if position.unrealized_pnl is None or position.unrealized_pnl > 0:
                            current_pnl = position.unrealized_pnl or 0
                            position.unrealized_pnl = current_pnl - abs(float(position.quantity) * 0.01)
                            adjusted_positions.append(position.id)
                
                self.db.commit()
            
            # Log adjustment to audit trail
            adjustment = TradingAdjustment(
                admin_user_id=admin_user_id,
                user_id=user_id,
                adjustment_type="win_rate",
                target_value=str(target_win_rate),
                previous_value=str(current_win_rate),
                result=f"Adjusted {len(adjusted_positions)} positions from {current_win_rate:.1f}% to {target_win_rate:.1f}%"
            )
            self.db.add(adjustment)
            self.db.commit()
            
            # Calculate new win rate
            new_win_rate = self._calculate_win_rate(user_id)
            
            logger.info(
                f"Win rate adjustment complete for user {user_id}: "
                f"{current_win_rate:.1f}% -> {new_win_rate:.1f}% "
                f"({len(adjusted_positions)} positions adjusted)"
            )
            
            return {
                "user_id": user_id,
                "previous_win_rate": current_win_rate,
                "target_win_rate": target_win_rate,
                "new_win_rate": new_win_rate,
                "positions_adjusted": len(adjusted_positions),
                "mode": mode,
                "adjustment_id": adjustment.id
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to adjust win rate for user {user_id}: {e}", exc_info=True)
            raise
    
    def _calculate_win_rate(self, user_id: int) -> float:
        """
        Calculate current win rate for user based on closed positions
        
        Args:
            user_id: User ID
            
        Returns:
            Win rate percentage (0-100)
        """
        from ..models.portfolio import PortfolioPosition
        
        # Get closed positions with P&L
        closed_positions = self.db.query(PortfolioPosition).filter(
            PortfolioPosition.user_id == user_id,
            PortfolioPosition.status == "closed",
            PortfolioPosition.realized_pnl.isnot(None)
        ).all()
        
        if not closed_positions:
            # No closed positions, calculate from open positions as proxy
            open_positions = self.db.query(PortfolioPosition).filter(
                PortfolioPosition.user_id == user_id,
                PortfolioPosition.status == "open",
                PortfolioPosition.unrealized_pnl.isnot(None)
            ).all()
            
            if not open_positions:
                return 50.0  # Default 50% if no data
            
            winning = [p for p in open_positions if p.unrealized_pnl and p.unrealized_pnl > 0]
            return (len(winning) / len(open_positions)) * 100
        
        # Calculate from closed positions
        winning_positions = [p for p in closed_positions if p.realized_pnl and p.realized_pnl > 0]
        win_rate = (len(winning_positions) / len(closed_positions)) * 100
        
        return round(win_rate, 2)
    
    def get_user_trading_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive trading statistics for user
        
        Args:
            user_id: User ID
            
        Returns:
            Trading statistics
        """
        from ..models.portfolio import PortfolioPosition
        
        all_positions = self.db.query(PortfolioPosition).filter(
            PortfolioPosition.user_id == user_id
        ).all()
        
        closed = [p for p in all_positions if p.status == "closed"]
        open_pos = [p for p in all_positions if p.status == "open"]
        
        total_realized_pnl = sum([p.realized_pnl for p in closed if p.realized_pnl]) or 0
        total_unrealized_pnl = sum([p.unrealized_pnl for p in open_pos if p.unrealized_pnl]) or 0
        
        winning_closed = [p for p in closed if p.realized_pnl and p.realized_pnl > 0]
        losing_closed = [p for p in closed if p.realized_pnl and p.realized_pnl < 0]
        
        return {
            "user_id": user_id,
            "total_positions": len(all_positions),
            "open_positions": len(open_pos),
            "closed_positions": len(closed),
            "win_rate": self._calculate_win_rate(user_id),
            "total_realized_pnl": float(total_realized_pnl),
            "total_unrealized_pnl": float(total_unrealized_pnl),
            "winning_trades": len(winning_closed),
            "losing_trades": len(losing_closed)
        }


def get_win_rate_controller(db: Session) -> WinRateController:
    """Get WinRateController instance"""
    return WinRateController(db)
