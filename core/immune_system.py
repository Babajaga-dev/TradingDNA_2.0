"""
Immune System Module - Core protection system for risk management and loss prevention.

This module implements automated defense mechanisms to protect trading operations
through dynamic risk management, stop losses, and noise filtering.
"""
from typing import Dict, List, Optional
import logging

from .immune_base import ImmuneBase, RiskMetrics, DefenseMetrics
from .immune_analysis import ImmuneAnalysis
from .immune_health import ImmuneHealth

logger = logging.getLogger(__name__)

class ImmuneSystem(ImmuneBase):
    """
    Main class implementing the immune system functionality for risk management
    and automated defense mechanisms.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the immune system with default parameters.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._analysis = ImmuneAnalysis(config)
        self._health = ImmuneHealth(config)
        logger.info("Immune System initialized with all components")

    def analyze_risk(self, positions: List[Dict]) -> RiskMetrics:
        """
        Analyze current risk exposure across all positions.

        Args:
            positions: List of current trading positions with their details

        Returns:
            RiskMetrics object containing calculated risk metrics
        """
        return self._analysis.analyze_risk(positions)

    def get_position_protection(
        self, 
        position: Dict,
        market_data: Optional[Dict] = None
    ) -> Dict[str, float]:
        """
        Get protection levels for a position.

        Args:
            position: Current position details
            market_data: Optional market data, uses internal state if not provided

        Returns:
            Dictionary containing protection levels and targets
        """
        return self._analysis.get_position_protection(position, market_data)

    def detect_extreme_events(self, market_data: Dict) -> bool:
        """
        Detect extreme market events like flash crashes or price manipulation.

        Args:
            market_data: Current market data including price and volume

        Returns:
            True if extreme event detected, False otherwise
        """
        return self._analysis.detect_extreme_events(market_data)

    def filter_signal(self, signal: Dict) -> Optional[Dict]:
        """
        Filter trading signals to remove noise and validate patterns.

        Args:
            signal: Trading signal to be validated

        Returns:
            Filtered signal if valid, None if rejected
        """
        return self._analysis.filter_signal(signal)

    def get_system_health(self) -> Dict[str, float]:
        """
        Get current health metrics of the immune system.

        Returns:
            Dictionary containing health metrics and their values
        """
        return self._health.get_system_health()

    def update_metrics(self, new_metrics: DefenseMetrics) -> None:
        """
        Update system performance metrics.

        Args:
            new_metrics: New metrics to update the system with
        """
        self._health.update_metrics(new_metrics)
        logger.info("Updated immune system metrics")