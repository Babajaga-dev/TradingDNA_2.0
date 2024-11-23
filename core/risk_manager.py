"""
Risk Manager Module - Handles risk assessment and management for the immune system.

This module implements risk calculation, exposure monitoring, and drawdown protection
mechanisms to ensure trading safety.
"""
from typing import Dict, List, Optional
import logging
from .risk_base import RiskBase, PositionRisk
from .risk_calculation import RiskCalculation
from .risk_protection import RiskProtection

logger = logging.getLogger(__name__)

class RiskManager(RiskBase):
    """
    Handles risk assessment and management for trading positions.
    Implements various risk metrics calculations and protection mechanisms.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the risk manager with configuration parameters.

        Args:
            config: Optional configuration dictionary with risk parameters
        """
        super().__init__(config)
        self._calculation = RiskCalculation(config)
        self._protection = RiskProtection(config)
        logger.info("Risk Manager initialized with all components")

    def calculate_position_risk(
        self,
        position: Dict,
        market_data: Dict,
        portfolio: Dict
    ) -> PositionRisk:
        """
        Calculate comprehensive risk metrics for a single position.

        Args:
            position: Position details including size and entry price
            market_data: Current market data including volatility
            portfolio: Current portfolio state including other positions

        Returns:
            PositionRisk object containing calculated risk metrics
        """
        return self._calculation.calculate_position_risk(position, market_data, portfolio)

    def calculate_position_size(
        self,
        available_capital: float,
        market_data: Dict
    ) -> float:
        """
        Calculate the appropriate position size based on fixed percentage.

        Args:
            available_capital: Total available capital
            market_data: Current market data including price and volatility

        Returns:
            Recommended position size in base currency
        """
        return self._calculation.calculate_position_size(available_capital, market_data)

    def check_risk_limits(
        self,
        position_risk: PositionRisk,
        portfolio: Dict
    ) -> bool:
        """
        Check if position risks are within acceptable limits.

        Args:
            position_risk: Calculated position risk metrics
            portfolio: Current portfolio state

        Returns:
            True if risks are acceptable, False otherwise
        """
        return self._calculation.check_risk_limits(position_risk, portfolio)

    def calculate_protection_levels(
        self,
        position: Dict,
        market_data: Dict
    ) -> Dict[str, float]:
        """
        Calculate comprehensive protection levels for a position.

        Args:
            position: Position details
            market_data: Current market data including volatility

        Returns:
            Dictionary containing protection levels and scaling targets
        """
        return self._protection.calculate_protection_levels(position, market_data)