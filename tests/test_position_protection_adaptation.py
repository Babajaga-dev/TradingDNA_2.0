"""Tests for the position protection market adaptation functionality.

This module contains unit tests for the market adaptation methods of PositionProtection class.
"""
import pytest
from typing import Dict
from core.position_protection import PositionProtection
from .test_position_protection_base import (
    protection,
    sample_position,
    sample_market_data
)

def test_adapt_to_market_conditions(protection: PositionProtection) -> None:
    """
    Test protection level adaptation to market conditions.
    
    Args:
        protection: PositionProtection instance
        
    Verifies:
        - Market trend impact on levels
        - Level adjustments direction
    """
    protection_levels: Dict[str, Any] = {
        'stop_loss': 38000.0,
        'warning_level': 38500.0,
        'take_profit': 42000.0,
        'trailing_stop': 41000.0,
        'scale_out_1': {'price': 41500.0, 'size': 0.25},
        'scale_in_1': {'price': 39000.0, 'size': 0.25}
    }
    
    # Test with uptrend
    uptrend_market = {'trend': 0.15, 'volatility': 0.1}
    up_levels = protection.adapt_to_market_conditions(
        protection_levels,
        uptrend_market
    )
    
    # Uptrend should adjust levels higher
    assert up_levels['stop_loss'] > protection_levels['stop_loss']
    assert up_levels['take_profit'] > protection_levels['take_profit']
    
    # Test with downtrend
    downtrend_market = {'trend': -0.15, 'volatility': 0.1}
    down_levels = protection.adapt_to_market_conditions(
        protection_levels,
        downtrend_market
    )
    
    # Downtrend should adjust levels lower
    assert down_levels['stop_loss'] < protection_levels['stop_loss']
    assert down_levels['take_profit'] < protection_levels['take_profit']

def test_protection_with_extreme_volatility(protection: PositionProtection) -> None:
    """
    Test protection calculation with extreme volatility.
    
    Args:
        protection: PositionProtection instance
        
    Verifies:
        - Max stop distance enforcement
        - Protection level adjustments
    """
    position = {'entry_price': 40000.0, 'size': 1.0}
    market_data = {
        'price': 41000.0,
        'volatility': 0.5,  # Extreme volatility
        'trend': 0.0
    }
    
    levels = protection.get_protection_levels(position, market_data)
    
    # Verify stop loss respects max_stop_distance
    max_stop_distance = position['entry_price'] * (
        1 - protection._config['max_stop_distance']
    )
    assert levels.stop_loss >= max_stop_distance

def test_protection_with_strong_trend(protection: PositionProtection) -> None:
    """
    Test protection calculation with strong market trend.
    
    Args:
        protection: PositionProtection instance
        
    Verifies:
        - Trend impact on protection levels
        - Level adjustments magnitude
    """
    position = {'entry_price': 40000.0, 'size': 1.0}
    market_data = {
        'price': 41000.0,
        'volatility': 0.15,
        'trend': 0.3  # Strong uptrend
    }
    
    levels = protection.get_protection_levels(position, market_data)
    
    # Compare with neutral trend
    neutral_levels = protection.get_protection_levels(
        position,
        {**market_data, 'trend': 0.0}
    )
    
    # Strong uptrend should result in higher targets
    assert levels.take_profit > neutral_levels.take_profit
    assert levels.trailing_stop > neutral_levels.trailing_stop