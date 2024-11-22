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
        logger.info("Immune System initialized with RiskManager")

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

    def calculate_dynamic_stops(
        self, 
        position: Dict,
        volatility: float
    ) -> Tuple[float, float]:
        """
        Calculate dynamic stop loss and take profit levels.

        Args:
            position: Current position details
            volatility: Current market volatility

        Returns:
            Tuple of (stop_loss_price, take_profit_price)
        """
        self._market_state['volatility'] = volatility
        protection = self._risk_manager.calculate_drawdown_protection(
            position,
            self._market_state
        )
        
        stop_loss = protection['stop_loss']
        take_profit = position['entry_price'] * (
            1 + (position['entry_price'] - stop_loss) / position['entry_price'] * 1.5
        )
        
        return stop_loss, take_profit

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
        """Assess counterparty risk based on position distribution."""
        # TODO: Implement counterparty risk assessment
        return 0.0

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
