"""
Immune System Module - Core protection system for risk management and loss prevention.

This module implements automated defense mechanisms to protect trading operations
through dynamic risk management, stop losses, and noise filtering.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from .risk_manager import RiskManager, PositionRisk

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

class ImmuneSystem:
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
            'risk_level': 'normal'
        }
        self._exchange_health = {}  # Track exchange health metrics
        logger.info("Immune System initialized with RiskManager")

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

    def analyze_risk(self, positions: List[Dict]) -> RiskMetrics:
        """
        Analyze current risk exposure across all positions.

        Args:
            positions: List of current trading positions with their details

        Returns:
            RiskMetrics object containing calculated risk metrics
        """
        portfolio = {
            'total_value': sum(
                pos['size'] * pos.get('current_price', pos['entry_price'])
                for pos in positions
            ),
            'positions': positions
        }

        total_risk = 0.0
        correlation_risk = 0.0
        
        for position in positions:
            risk = self._risk_manager.calculate_position_risk(
                position,
                self._market_state,
                portfolio
            )
            total_risk += risk.total_risk
            correlation_risk += risk.correlation_risk

        return RiskMetrics(
            total_exposure=total_risk / len(positions) if positions else 0.0,
            drawdown=self._calculate_drawdown(positions),
            counterparty_risk=self._assess_counterparty_risk(positions),
            asset_correlation=correlation_risk / len(positions) if positions else 0.0
        )

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
        if market_data is None:
            market_data = self._market_state

        return self._risk_manager.calculate_protection_levels(position, market_data)

    def detect_extreme_events(self, market_data: Dict) -> bool:
        """
        Detect extreme market events like flash crashes or price manipulation.

        Args:
            market_data: Current market data including price and volume

        Returns:
            True if extreme event detected, False otherwise
        """
        self._update_market_state(market_data)
        
        # Check for extreme price movements
        if 'previous_price' in self._market_state:
            price_change = abs(
                market_data['price'] / self._market_state['previous_price'] - 1
            )
            if price_change > 0.1:  # 10% price movement
                logger.warning(f"Extreme price movement detected: {price_change:.2%}")
                return True
        
        # Check for volume anomalies
        if market_data.get('volume', 0) > self._market_state.get('avg_volume', 0) * 3:
            logger.warning("Abnormal volume detected")
            return True
            
        return False

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
            
        if self._market_state['risk_level'] == 'high' and signal['type'] == 'LONG':
            logger.info("Long signal rejected due to high risk environment")
            return None
            
        return signal

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

    def _calculate_drawdown(self, positions: List[Dict]) -> float:
        """Calculate current drawdown across all positions."""
        total_pnl = sum(
            pos.get('unrealized_pnl', 0) for pos in positions
        )
        total_value = sum(
            pos['size'] * pos.get('current_price', pos['entry_price'])
            for pos in positions
        )
        return abs(min(0, total_pnl / total_value)) if total_value else 0

    def _assess_counterparty_risk(self, positions: List[Dict]) -> float:
        """
        Assess counterparty risk based on exchange health and position distribution.
        
        Args:
            positions: List of current trading positions

        Returns:
            Normalized counterparty risk score between 0 and 1
        """
        if not positions:
            return 0.0
            
        # Calculate risk per exchange
        exchange_risks = {}
        for position in positions:
            exchange = position.get('exchange', 'unknown')
            if exchange not in exchange_risks:
                exchange_risks[exchange] = {
                    'total_value': 0.0,
                    'positions': 0,
                    'health_score': self._get_exchange_health_score(exchange)
                }
            
            position_value = position['size'] * position.get(
                'current_price',
                position['entry_price']
            )
            exchange_risks[exchange]['total_value'] += position_value
            exchange_risks[exchange]['positions'] += 1
        
        # Calculate total portfolio value
        total_value = sum(
            ex['total_value'] for ex in exchange_risks.values()
        )
        
        if total_value == 0:
            return 0.0
            
        # Calculate weighted risk score
        total_risk = 0.0
        for ex_risk in exchange_risks.values():
            # Weight by portfolio percentage and health score
            weight = ex_risk['total_value'] / total_value
            concentration_penalty = min(1.0, ex_risk['positions'] / 5)  # Penalize concentration
            risk_score = (1 - ex_risk['health_score']) * concentration_penalty
            total_risk += weight * risk_score
            
        return min(1.0, total_risk)

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
        
        # Calculate final score
        score = (
            uptime * 0.4 +
            response_score * 0.3 +
            (1 - error_rate) * 0.3
        )
        
        return max(0.0, min(1.0, score))

    def _update_market_state(self, market_data: Dict) -> None:
        """Update internal market state with new data."""
        self._market_state.update({
            'previous_price': self._market_state.get('price', market_data['price']),
            'price': market_data['price'],
            'volume': market_data.get('volume', 0),
            'volatility': market_data.get('volatility', 
                                        self._market_state['volatility'])
        })

    def _calculate_risk_health(self) -> float:
        """Calculate health of risk management components."""
        return 1.0 - self._metrics.false_positive_rate

    def _calculate_defense_efficiency(self) -> float:
        """Calculate efficiency of defense mechanisms."""
        return self._metrics.protection_efficiency

    def _calculate_system_stability(self) -> float:
        """Calculate overall system stability."""
        return self._metrics.system_stability
