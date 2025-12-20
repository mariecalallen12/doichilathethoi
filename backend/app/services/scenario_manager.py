"""
Market Scenario Manager Service
Quản lý và áp dụng các kịch bản thị trường vào simulation
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ScenarioManager:
    """Service to manage market scenarios"""
    
    def __init__(self):
        self.current_scenario: Optional[Dict] = None
        self.broadcaster = None
        
    def set_broadcaster(self, broadcaster):
        """Set trade broadcaster reference"""
        self.broadcaster = broadcaster
        
    def apply_scenario(self, scenario_id: int, db: Session) -> Dict[str, Any]:
        """
        Apply a market scenario to simulation
        
        Args:
            scenario_id: ID của scenario
            db: Database session
            
        Returns:
            Scenario details
        """
        from ..models.market import MarketScenario
        
        scenario = db.query(MarketScenario).filter_by(id=scenario_id).first()
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
            
        config = scenario.config or {}
        
        logger.info(f"Applying scenario: {scenario.name} (ID: {scenario_id})")
        
        # Update trade broadcaster parameters
        if self.broadcaster and hasattr(self.broadcaster, 'set_volatility'):
            volatility = config.get("volatility", 0.005)
            self.broadcaster.set_volatility(volatility)
            logger.info(f"Set volatility to {volatility}")
            
            trend = config.get("trend", "sideways")
            self.broadcaster.set_trend(trend)
            logger.info(f"Set trend to {trend}")
            
            volume_multiplier = config.get("volume_multiplier", 1.0)
            self.broadcaster.set_volume_multiplier(volume_multiplier)
            logger.info(f"Set volume multiplier to {volume_multiplier}")
        
        # Mark scenario as active (deactivate others)
        db.query(MarketScenario).update({"is_active": False})
        scenario.is_active = True
        db.commit()
        db.refresh(scenario)
        
        self.current_scenario = {
            "id": scenario.id,
            "name": scenario.name,
            "type": scenario.scenario_type,
            "config": config
        }
        
        logger.info(f"Scenario {scenario.name} applied successfully")
        
        return {
            "id": scenario.id,
            "name": scenario.name,
            "description": scenario.description,
            "scenario_type": scenario.scenario_type,
            "config": config,
            "is_active": scenario.is_active
        }
        
    def stop_scenario(self, db: Session):
        """
        Stop active scenario, return to normal
        
        Args:
            db: Database session
        """
        from ..models.market import MarketScenario
        
        logger.info("Stopping active scenario")
        
        # Deactivate all scenarios
        db.query(MarketScenario).update({"is_active": False})
        db.commit()
        
        self.current_scenario = None
        
        # Reset broadcaster to defaults
        if self.broadcaster and hasattr(self.broadcaster, 'reset_to_defaults'):
            self.broadcaster.reset_to_defaults()
            logger.info("Broadcaster reset to defaults")
            
    def get_active_scenario(self, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get currently active scenario
        
        Args:
            db: Database session
            
        Returns:
            Active scenario or None
        """
        from ..models.market import MarketScenario
        
        scenario = db.query(MarketScenario).filter_by(is_active=True).first()
        
        if scenario:
            return {
                "id": scenario.id,
                "name": scenario.name,
                "description": scenario.description,
                "scenario_type": scenario.scenario_type,
                "config": scenario.config,
                "is_active": scenario.is_active
            }
        
        return None


# Singleton instance
_scenario_manager: Optional[ScenarioManager] = None


def get_scenario_manager() -> ScenarioManager:
    """Get scenario manager instance (singleton)"""
    global _scenario_manager
    
    if _scenario_manager is None:
        _scenario_manager = ScenarioManager()
        
        # Connect to trade broadcaster if available
        try:
            from .trade_broadcaster import get_trade_broadcaster
            broadcaster = get_trade_broadcaster()
            _scenario_manager.set_broadcaster(broadcaster)
        except Exception as e:
            logger.warning(f"Could not connect to trade broadcaster: {e}")
    
    return _scenario_manager
