"""
Health monitoring module for the Immune System - System health and performance metrics.
"""
from typing import Dict
import logging
from .immune_base import ImmuneBase, DefenseMetrics

logger = logging.getLogger(__name__)

class ImmuneHealth(ImmuneBase):
    """Class implementing health monitoring and performance metrics."""

    def get_system_health(self) -> Dict[str, float]:
        """
        Get current health metrics of the immune system.

        Returns:
            Dictionary containing health metrics and their values
        """
        return {
            'risk_management': self._calculate_risk_health(),
            'defense_efficiency': self._calculate_defense_efficiency(),
            'system_stability': self._calculate_system_stability()
        }

    def update_metrics(self, new_metrics: DefenseMetrics) -> None:
        """
        Update system performance metrics.

        Args:
            new_metrics: New metrics to update the system with
        """
        self._metrics = new_metrics
        logger.info(f"Updated immune system metrics: {new_metrics}")

    def _calculate_risk_health(self) -> float:
        """
        Calculate health of risk management components.
        
        Returns:
            Health score between 0 and 1
        """
        return 1.0 - self._metrics.false_positive_rate

    def _calculate_defense_efficiency(self) -> float:
        """
        Calculate efficiency of defense mechanisms.
        
        Returns:
            Efficiency score between 0 and 1
        """
        return self._metrics.protection_efficiency

    def _calculate_system_stability(self) -> float:
        """
        Calculate overall system stability.
        
        Returns:
            Stability score between 0 and 1
        """
        return self._metrics.system_stability