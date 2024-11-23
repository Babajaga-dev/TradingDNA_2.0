"""
Base module for Risk Management - Core configuration and initialization.
"""
from typing import Dict, Optional
from dataclasses import dataclass
import logging
from .position_protection import PositionProtection

logger = logging.getLogger(__name__)

@dataclass
class PositionRisk:
    """Container for position-specific risk metrics."""
    exposure: float
    volatility_risk: float
    correlation_risk: float
    total_risk: float
    var_risk: float

@dataclass
class ProtectionConfig:
    """Configuration for protection mechanisms."""
    dynamic_stops: bool = True
    profit_protection: bool = True
    position_scaling: bool = True
    market_adaptation: bool = True

class RiskBase:
    """Base class for risk management functionality."""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the risk manager with configuration parameters.

        Args:
            config: Optional configuration dictionary with risk parameters
        """
        self._config = config or {
            'max_position_size': 0.1,  # 10% of capital
            'max_total_exposure': 0.2,  # 20% of capital
            'correlation_threshold': 0.7,
            'max_drawdown': 0.1,  # 10% drawdown limit
            'volatility_multiplier': 2.0,
            'var_confidence': 0.98,  # 98% confidence for VaR
            'position_size_fixed': 0.02,  # 2% of capital per position
            'profit_take_multiplier': 1.5,  # Take profit at 1.5x stop distance
            'trailing_stop_activation': 0.5,  # Activate trailing stop at 50% of take profit
            'position_scale_threshold': 0.3,  # Scale position at 30% profit
            'market_trend_threshold': 0.1,  # Market trend significance threshold
            'min_profit_target': 0.02,  # 2% minimum profit target
            'max_stop_distance': 0.05,  # 5% maximum stop distance
            'scale_out_steps': 3,  # Number of scale out levels
            'scale_ratio': 0.25  # Ratio to scale at each level
        }
        self._protection = ProtectionConfig()
        self._position_protection = PositionProtection(self._config)
        logger.info("Risk Manager initialized with config: %s", self._config)

    def set_protection_config(self, protection_config: Dict[str, bool]) -> None:
        """
        Configure protection mechanisms.

        Args:
            protection_config: Dictionary with protection settings
                - dynamic_stops: Enable/disable dynamic stop losses
                - profit_protection: Enable/disable profit protection
                - position_scaling: Enable/disable position scaling
                - market_adaptation: Enable/disable market adaptation
        """
        self._protection = ProtectionConfig(
            dynamic_stops=protection_config.get('dynamic_stops', True),
            profit_protection=protection_config.get('profit_protection', True),
            position_scaling=protection_config.get('position_scaling', True),
            market_adaptation=protection_config.get('market_adaptation', True)
        )
        logger.info("Protection configuration updated: %s", self._protection)

    def get_protection_config(self) -> Dict[str, bool]:
        """
        Get current protection configuration.

        Returns:
            Dictionary with current protection settings
        """
        return {
            'dynamic_stops': self._protection.dynamic_stops,
            'profit_protection': self._protection.profit_protection,
            'position_scaling': self._protection.position_scaling,
            'market_adaptation': self._protection.market_adaptation
        }