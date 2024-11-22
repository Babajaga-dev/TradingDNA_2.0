"""
Position Protection Module - Implements advanced position protection mechanisms.

This module provides specialized protection strategies including dynamic stops,
profit targets, position scaling and market adaptation mechanisms.
"""
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import logging
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

@dataclass
class ProtectionLevels:
    """Container for position protection levels."""
    stop_loss: float
    warning_level: float
    take_profit: float
    trailing_stop: float
    scale_out_level: float
    scale_in_level: float

class PositionProtection:
    """
    Implements advanced position protection mechanisms including
    dynamic stops, profit targets and position scaling.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize protection mechanisms with configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {
            'volatility_multiplier': 2.0,
            'profit_take_multiplier': 1.5,
            'trailing_stop_activation': 0.5,
            'position_scale_threshold': 0.3,
            'market_trend_threshold': 0.1,
            'min_profit_target': 0.02,  # 2% minimum profit target
            'max_stop_distance': 0.05,   # 5% maximum stop distance
            'scale_out_steps': 3,        # Number of scale out levels
            'scale_ratio': 0.25          # Ratio to scale at each level
        }
        logger.info("Position Protection initialized with config: %s", self._config)

    def calculate_dynamic_stops(
        self,
        entry_price: float,
        current_price: float,
        volatility: float
    ) -> Tuple[float, float]:
        """
        Calculate dynamic stop loss and warning levels based on volatility.
        
        Args:
            entry_price: Position entry price
            current_price: Current market price
            volatility: Current market volatility
            
        Returns:
            Tuple of (stop_loss, warning_level)
        """
        # Base stop distance adjusted by volatility
        base_distance = self._config['max_stop_distance']
        volatility_factor = 1 + (volatility * self._config['volatility_multiplier'])
        stop_distance = base_distance * volatility_factor
        
        # Calculate stop levels from current price
        stop_loss = current_price * (1 - stop_distance)
        warning_level = current_price * (1 - stop_distance * 0.7)
        
        # Ensure minimum distance from entry
        min_stop = entry_price * (1 - self._config['max_stop_distance'])
        stop_loss = max(stop_loss, min_stop)
        warning_level = max(warning_level, min_stop * 1.02)
        
        return stop_loss, warning_level

    def calculate_profit_targets(
        self,
        entry_price: float,
        stop_loss: float,
        market_trend: float
    ) -> Tuple[float, float]:
        """
        Calculate take profit and trailing stop activation levels.
        
        Args:
            entry_price: Position entry price
            stop_loss: Current stop loss level
            market_trend: Current market trend indicator
            
        Returns:
            Tuple of (take_profit, trailing_activation)
        """
        # Calculate base risk percentage
        risk_percent = abs(entry_price - stop_loss) / entry_price
        
        # Adjust multipliers based on market trend
        trend_adjustment = max(0.8, min(1.2, 1 + market_trend))
        
        # Calculate base target percentages from min_profit_target
        base_take_profit = self._config['min_profit_target']
        base_trailing = self._config['min_profit_target'] * 0.75
        
        # Add risk-based component
        take_profit_percent = (base_take_profit + risk_percent) * self._config['profit_take_multiplier'] * trend_adjustment
        trailing_percent = (base_trailing + risk_percent * 0.5) * self._config['trailing_stop_activation'] * trend_adjustment
        
        # Calculate absolute levels
        take_profit = entry_price * (1 + take_profit_percent)
        trailing_activation = entry_price * (1 + trailing_percent)
        
        # Ensure trailing stop is below take profit but above entry
        trailing_activation = min(take_profit * 0.9, trailing_activation)
        trailing_activation = max(trailing_activation, entry_price * 1.005)  # At least 0.5% above entry
        
        return take_profit, trailing_activation

    def calculate_scaling_levels(
        self,
        entry_price: float,
        position_size: float,
        market_volatility: float
    ) -> Dict[str, float]:
        """
        Calculate position scaling levels for gradual position management.
        
        Args:
            entry_price: Position entry price
            position_size: Current position size
            market_volatility: Current market volatility
            
        Returns:
            Dictionary containing scale out and scale in levels with sizes
        """
        # Adjust scale threshold based on volatility
        scale_threshold = self._config['position_scale_threshold'] * (
            1 + market_volatility
        )
        
        # Calculate base levels
        scale_out_base = entry_price * (1 + scale_threshold)
        scale_in_base = entry_price * (1 - scale_threshold)
        
        # Calculate scaling steps
        scale_levels = {}
        step_size = position_size * self._config['scale_ratio']
        
        for i in range(self._config['scale_out_steps']):
            # Scale out levels (take profit scaling)
            level_price = scale_out_base * (1 + (i * 0.5 * scale_threshold))
            scale_levels[f'scale_out_{i+1}'] = {
                'price': level_price,
                'size': step_size
            }
            
            # Scale in levels (averaging down)
            level_price = scale_in_base * (1 - (i * 0.5 * scale_threshold))
            scale_levels[f'scale_in_{i+1}'] = {
                'price': level_price,
                'size': step_size
            }
            
        return scale_levels

    def adapt_to_market_conditions(
        self,
        protection_levels: Dict[str, float],
        market_data: Dict
    ) -> Dict[str, float]:
        """
        Adapt protection levels based on current market conditions.
        
        Args:
            protection_levels: Current protection levels
            market_data: Current market conditions including trend and volatility
            
        Returns:
            Adjusted protection levels
        """
        trend = market_data.get('trend', 0)
        volatility = market_data.get('volatility', 0)
        
        # Only adapt if trend is significant
        if abs(trend) > self._config['market_trend_threshold']:
            # Calculate adjustment factor
            adjustment = trend * volatility
            
            # Adjust all levels
            adjusted_levels = {}
            for level_name, level_value in protection_levels.items():
                if isinstance(level_value, dict):
                    # Handle scaling levels
                    adjusted_levels[level_name] = {
                        'price': level_value['price'] * (1 + adjustment),
                        'size': level_value['size']
                    }
                else:
                    # Handle simple price levels
                    adjusted_levels[level_name] = level_value * (1 + adjustment)
                    
            return adjusted_levels
            
        return protection_levels

    def get_protection_levels(
        self,
        position: Dict,
        market_data: Dict
    ) -> ProtectionLevels:
        """
        Calculate all protection levels for a position.
        
        Args:
            position: Position details including entry price and size
            market_data: Current market data including price and conditions
            
        Returns:
            ProtectionLevels object with all calculated levels
        """
        entry_price = position['entry_price']
        current_price = market_data.get('price', entry_price)
        volatility = market_data.get('volatility', 0)
        market_trend = market_data.get('trend', 0)
        
        # With minimal data, use entry price as reference
        reference_price = entry_price if len(market_data) <= 1 else current_price
        
        # Calculate base protection levels
        stop_loss, warning_level = self.calculate_dynamic_stops(
            entry_price,
            reference_price,
            volatility
        )
        
        take_profit, trailing_stop = self.calculate_profit_targets(
            entry_price,
            stop_loss,
            market_trend
        )
        
        scaling_levels = self.calculate_scaling_levels(
            entry_price,
            position['size'],
            volatility
        )
        
        # Combine all levels
        protection_levels = {
            'stop_loss': stop_loss,
            'warning_level': warning_level,
            'take_profit': take_profit,
            'trailing_stop': trailing_stop,
            **scaling_levels
        }
        
        # Adapt to market conditions
        adjusted_levels = self.adapt_to_market_conditions(
            protection_levels,
            market_data
        )
        
        return ProtectionLevels(
            stop_loss=adjusted_levels['stop_loss'],
            warning_level=adjusted_levels['warning_level'],
            take_profit=adjusted_levels['take_profit'],
            trailing_stop=adjusted_levels['trailing_stop'],
            scale_out_level=adjusted_levels['scale_out_1']['price'],
            scale_in_level=adjusted_levels['scale_in_1']['price']
        )