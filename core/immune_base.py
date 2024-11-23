"""
Base module for the Immune System - Core protection system initialization and configuration.
"""
from typing import Dict, Optional
import logging
from dataclasses import dataclass
from .risk_manager import RiskManager

logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    """Container for risk-related metrics."""
    total_exposure: float
    drawdown: float
    counterparty_risk: float
    asset_correlation: float

@dataclass
class DefenseMetrics:
    """Container for defense-related performance metrics."""
    false_positive_rate: float
    reaction_time: float
    protection_efficiency: float
    system_stability: float

class ImmuneBase:
    """Base class implementing core immune system functionality."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the immune system with default parameters.
        
        Args:
            config: Optional configuration dictionary
        """
        self._risk_manager = RiskManager(config)
        self._metrics = DefenseMetrics(
            false_positive_rate=0.0,
            reaction_time=0.0,
            protection_efficiency=0.0,
            system_stability=0.0
        )
        self._market_state = {
            'volatility': 0.0,
            'trend': 'neutral',
            'risk_level': 'normal',
            'avg_volume': 0.0
        }
        self._exchange_health = {}
        logger.info("Immune System initialized with RiskManager")

    def calculate_dynamic_stops(self, position: Dict, volatility: float) -> tuple[float, float]:
        """
        Calculate dynamic stop loss and take profit levels based on position and market volatility.
        
        Args:
            position: Current position details including entry price and price history
            volatility: Current market volatility
            
        Returns:
            Tuple of (stop_loss_price, take_profit_price)
        """
        entry_price = position['entry_price']
        
        # Base stop distance on volatility and recent price movement
        volatility_factor = max(0.5, min(2.0, volatility * 10))
        price_history = position.get('price_history', [])
        
        if price_history:
            # Calculate average true range from price history
            ranges = [abs(high - low) for high, low in zip(price_history[1:], price_history[:-1])]
            avg_range = sum(ranges) / len(ranges) if ranges else entry_price * 0.01
            
            # Dynamic stop loss distance based on ATR and volatility
            stop_distance = avg_range * volatility_factor
            take_profit_distance = stop_distance * 1.5  # Risk:Reward ratio of 1:1.5
        else:
            # Fallback to simple percentage if no price history
            stop_distance = entry_price * 0.02 * volatility_factor
            take_profit_distance = stop_distance * 1.5
        
        stop_loss = entry_price - stop_distance
        take_profit = entry_price + take_profit_distance
        
        logger.info(f"Calculated dynamic stops - SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
        return stop_loss, take_profit

    def set_protection_config(self, config: Dict[str, bool]) -> None:
        """
        Configure protection mechanisms.

        Args:
            config: Dictionary with protection settings
                - dynamic_stops: Enable/disable dynamic stop losses
                - profit_protection: Enable/disable profit protection
                - position_scaling: Enable/disable position scaling
                - market_adaptation: Enable/disable market adaptation
        """
        self._risk_manager.set_protection_config(config)
        logger.info("Updated protection configuration: %s", config)

    def get_protection_config(self) -> Dict[str, bool]:
        """
        Get current protection configuration.

        Returns:
            Dictionary with current protection settings
        """
        return self._risk_manager.get_protection_config()

    def _update_market_state(self, market_data: Dict) -> None:
        """Update internal market state with new data."""
        self._market_state.update({
            'previous_price': self._market_state.get('price', market_data['price']),
            'price': market_data['price'],
            'volume': market_data.get('volume', 0),
            'volatility': market_data.get('volatility', 
                                        self._market_state['volatility'])
        })