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
        self._market_state = {
            'risk_level': 'normal',
            'volatility': 0.0,
            'avg_volume': 0.0
        }
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
        if signal.get('confidence', 0) < 0.7:
            logger.info("Signal rejected due to low confidence")
            return None
            
        if self._market_state['risk_level'] == 'high':
            logger.info("Signal rejected due to high risk environment")
            return None
            
        return signal

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
        self._metrics = new_metrics  # Update local metrics
        self._health.update_metrics(new_metrics)  # Update health component metrics
        logger.info("Updated immune system metrics")

    def _assess_counterparty_risk(self, positions: List[Dict]) -> float:
        """
        Assess counterparty risk based on exchange health and position distribution.
        
        Args:
            positions: List of current trading positions

        Returns:
            Normalized counterparty risk score between 0 and 1
        """
        return self._analysis._assess_counterparty_risk(positions)

    def _get_exchange_health_score(self, exchange: str) -> float:
        """
        Get health score for a specific exchange.
        
        Args:
            exchange: Exchange identifier

        Returns:
            Health score between 0 and 1, where 1 is perfectly healthy
        """
        if exchange not in self._exchange_health:
            return 0.8  # Default score for unknown exchanges
            
        health = self._exchange_health[exchange]
        
        # Calculate health score based on various metrics
        uptime = health.get('uptime', 0.95)
        api_response_time = health.get('api_response_time', 500)  # ms
        error_rate = health.get('error_rate', 0.05)
        
        # Normalize response time (0-1000ms -> 1-0)
        response_score = max(0, 1 - (api_response_time / 1000))
        
        # Calculate final score with weighted components
        score = (
            uptime * 0.4 +  # 40% weight on uptime
            response_score * 0.3 +  # 30% weight on response time
            (1 - error_rate) * 0.3  # 30% weight on error rate
        )
        
        return max(0.0, min(1.0, score))

    def _calculate_drawdown(self, positions: List[Dict]) -> float:
        """
        Calculate current drawdown across all positions.
        
        Args:
            positions: List of current trading positions

        Returns:
            Current drawdown as a ratio between 0 and 1
        """
        return self._analysis._calculate_drawdown(positions)

    def _update_market_state(self, market_data: Dict) -> None:
        """
        Update internal market state with new data.
        
        Args:
            market_data: New market data including price, volume, and volatility
        """
        self._market_state.update({
            'previous_price': self._market_state.get('price', market_data['price']),
            'price': market_data['price'],
            'volume': market_data.get('volume', 0),
            'volatility': market_data.get('volatility', self._market_state['volatility'])
        })
