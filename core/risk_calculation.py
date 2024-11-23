"""
Risk Calculation Module - Handles risk metrics calculation and analysis.
"""
from typing import Dict, List
import logging
import numpy as np
from scipy import stats
from .risk_base import RiskBase, PositionRisk

logger = logging.getLogger(__name__)

class RiskCalculation(RiskBase):
    """Class implementing risk calculation and analysis."""

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
        exposure = self._calculate_exposure(position, portfolio)
        vol_risk = self._calculate_volatility_risk(position, market_data)
        corr_risk = self._calculate_correlation_risk(position, portfolio)
        var_risk = self._calculate_var_risk(position, market_data)
        
        total_risk = self._aggregate_risk_metrics(
            exposure,
            vol_risk,
            corr_risk,
            var_risk
        )

        return PositionRisk(
            exposure=exposure,
            volatility_risk=vol_risk,
            correlation_risk=corr_risk,
            total_risk=total_risk,
            var_risk=var_risk
        )

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
        fixed_size = available_capital * self._config['position_size_fixed']
        
        if self._protection.position_scaling:
            # Adjust for volatility
            volatility = market_data.get('volatility', 0.0)
            volatility_adjustment = max(0.5, 1 - volatility)
            fixed_size *= volatility_adjustment
        
        # Ensure we don't exceed max position size
        max_size = available_capital * self._config['max_position_size']
        position_size = min(fixed_size, max_size)
        
        return position_size

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
        if position_risk.total_risk > self._config['max_position_size']:
            logger.warning("Position risk exceeds maximum allowed")
            return False

        total_exposure = self._calculate_total_exposure(portfolio)
        if total_exposure > self._config['max_total_exposure']:
            logger.warning("Total exposure exceeds maximum allowed")
            return False

        if position_risk.correlation_risk > self._config['correlation_threshold']:
            logger.warning("Correlation risk exceeds threshold")
            return False

        return True

    def _calculate_exposure(self, position: Dict, portfolio: Dict) -> float:
        """Calculate position exposure relative to portfolio."""
        position_value = position['size'] * position.get('current_price', 
                                                       position['entry_price'])
        portfolio_value = portfolio.get('total_value', 0)
        return position_value / portfolio_value if portfolio_value else 0

    def _calculate_volatility_risk(
        self,
        position: Dict,
        market_data: Dict
    ) -> float:
        """Calculate risk based on market volatility."""
        volatility = market_data.get('volatility', 0.0)
        return volatility * position['size']

    def _calculate_correlation_risk(
        self,
        position: Dict,
        portfolio: Dict
    ) -> float:
        """
        Calculate risk based on asset correlation with portfolio.
        
        Uses price history to calculate correlation between the position's
        asset and other assets in the portfolio.
        """
        if not portfolio.get('positions'):
            return 0.0
            
        # Get price history for position's asset
        position_returns = position.get('price_history', [])
        if not position_returns:
            return 0.0
            
        # Calculate correlations with other positions
        correlations = []
        for other_pos in portfolio['positions']:
            if other_pos['symbol'] == position['symbol']:
                continue
                
            other_returns = other_pos.get('price_history', [])
            if not other_returns:
                continue
                
            # Ensure equal length
            min_len = min(len(position_returns), len(other_returns))
            if min_len < 2:
                continue
                
            correlation = np.corrcoef(
                position_returns[:min_len],
                other_returns[:min_len]
            )[0, 1]
            
            correlations.append(abs(correlation))
            
        return max(correlations) if correlations else 0.0

    def _calculate_var_risk(
        self,
        position: Dict,
        market_data: Dict
    ) -> float:
        """
        Calculate Value at Risk for the position.
        
        Uses historical price data to calculate VaR at the configured
        confidence level.
        """
        price_history = position.get('price_history', [])
        if not price_history or len(price_history) < 2:
            return 0.0
            
        # Calculate returns
        returns = np.diff(price_history) / price_history[:-1]
        
        # Calculate VaR
        var = stats.norm.ppf(
            1 - self._config['var_confidence'],
            np.mean(returns),
            np.std(returns)
        )
        
        # Normalize to 0-1 range
        return min(1.0, abs(var))

    def _calculate_total_exposure(self, portfolio: Dict) -> float:
        """Calculate total portfolio exposure."""
        return sum(
            pos['size'] * pos.get('current_price', pos['entry_price'])
            for pos in portfolio.get('positions', [])
        ) / portfolio.get('total_value', 1)

    def _aggregate_risk_metrics(
        self,
        exposure: float,
        volatility_risk: float,
        correlation_risk: float,
        var_risk: float
    ) -> float:
        """
        Aggregate different risk metrics into a single risk score.

        Uses a weighted average of different risk metrics to produce
        a final risk score between 0 and 1.
        """
        weights = {
            'exposure': 0.3,
            'volatility': 0.3,
            'correlation': 0.2,
            'var': 0.2
        }
        
        return (
            exposure * weights['exposure'] +
            volatility_risk * weights['volatility'] +
            correlation_risk * weights['correlation'] +
            var_risk * weights['var']
        )