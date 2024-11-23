"""
Risk Protection Module - Handles protection levels and mechanisms.
"""
from typing import Dict, Optional
import logging
from .risk_base import RiskBase

logger = logging.getLogger(__name__)

class RiskProtection(RiskBase):
    """Class implementing protection mechanisms and levels."""

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
        if not any([
            self._protection.dynamic_stops,
            self._protection.profit_protection,
            self._protection.position_scaling,
            self._protection.market_adaptation
        ]):
            logger.warning("All protection mechanisms are disabled")
            return {}

        protection_levels = self._position_protection.get_protection_levels(
            position,
            market_data
        )

        result = {
            'stop_loss': protection_levels.stop_loss,
            'warning_level': protection_levels.warning_level,
            'take_profit': protection_levels.take_profit,
            'trailing_stop': protection_levels.trailing_stop,
            'scale_out_level': protection_levels.scale_out_level,
            'scale_in_level': protection_levels.scale_in_level
        }

        logger.info(
            "Calculated protection levels for position: %s",
            {k: round(v, 4) for k, v in result.items()}
        )

        return result