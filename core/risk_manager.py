"""
Risk Manager Module - Handles risk assessment and management for the immune system.

This module implements risk calculation, exposure monitoring, and drawdown protection
mechanisms to ensure trading safety.
"""
from typing import Dict, List, Optional, Union
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

    def __init__(self, config: Optional[Dict[str, Union[float, bool]]] = None) -> None:
        """
        Initialize the risk manager with configuration parameters.

        Args:
            config: Optional configuration dictionary with risk parameters
                   Contains keys like max_position_size, max_total_exposure, etc.
        """
        super().__init__(config)
        self._calculation = RiskCalculation(config)
        self._protection = RiskProtection(config)
        logger.info("Risk Manager initialized with all components")

    def calculate_position_risk(
        self,
        position: Dict[str, Union[str, float, List[float]]],
        market_data: Dict[str, Union[float, int]],
        portfolio: Dict[str, Union[float, List[Dict]]]
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
        market_data: Dict[str, Union[float, int]]
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
        portfolio: Dict[str, Union[float, List[Dict]]]
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
        position: Dict[str, Union[str, float, List[float]]],
        market_data: Dict[str, Union[float, int]]
    ) -> Dict[str, float]:
        """
        Calculate comprehensive protection levels for a position.

        Args:
            position: Position details including current price and history
            market_data: Current market data including volatility

        Returns:
            Dictionary containing protection levels and scaling targets
        """
        return self._protection.calculate_protection_levels(position, market_data)

    def _calculate_exposure(
        self,
        position: Dict[str, Union[str, float, List[float]]],
        portfolio: Dict[str, Union[float, List[Dict]]]
    ) -> float:
        """
        Calculate position exposure relative to portfolio.

        Args:
            position: Position details including size and prices
            portfolio: Current portfolio state with total value

        Returns:
            Exposure ratio between 0 and 1
        """
        return self._calculation._calculate_exposure(position, portfolio)

    def _calculate_volatility_risk(
        self,
        position: Dict[str, Union[str, float, List[float]]],
        market_data: Dict[str, Union[float, int]]
    ) -> float:
        """
        Calculate risk based on market volatility.

        Args:
            position: Position details including size
            market_data: Market data including volatility metric

        Returns:
            Volatility risk score between 0 and 1
        """
        return self._calculation._calculate_volatility_risk(position, market_data)

    def _calculate_correlation_risk(
        self,
        position: Dict[str, Union[str, float, List[float]]],
        portfolio: Dict[str, Union[float, List[Dict]]]
    ) -> float:
        """
        Calculate correlation risk with other portfolio positions.

        Args:
            position: Position details including price history
            portfolio: Portfolio state including other positions

        Returns:
            Correlation risk score between 0 and 1
        """
        return self._calculation._calculate_correlation_risk(position, portfolio)

    def _calculate_var_risk(
        self,
        position: Dict[str, Union[str, float, List[float]]],
        market_data: Dict[str, Union[float, int]]
    ) -> float:
        """
        Calculate Value at Risk for the position.

        Args:
            position: Position details including price history
            market_data: Market data including volatility

        Returns:
            VaR risk score between 0 and 1
        """
        return self._calculation._calculate_var_risk(position, market_data)

    def _calculate_total_exposure(
        self,
        portfolio: Dict[str, Union[float, List[Dict]]]
    ) -> float:
        """
        Calculate total portfolio exposure.

        Args:
            portfolio: Portfolio state including all positions

        Returns:
            Total exposure ratio between 0 and 1
        """
        return self._calculation._calculate_total_exposure(portfolio)

    def _aggregate_risk_metrics(
        self,
        exposure: float,
        volatility_risk: float,
        correlation_risk: float,
        var_risk: float
    ) -> float:
        """
        Aggregate multiple risk metrics into a single score.

        Args:
            exposure: Position exposure ratio
            volatility_risk: Volatility-based risk score
            correlation_risk: Correlation with portfolio score
            var_risk: Value at Risk score

        Returns:
            Aggregated risk score between 0 and 1
        """
        return self._calculation._aggregate_risk_metrics(
            exposure,
            volatility_risk,
            correlation_risk,
            var_risk
        )
