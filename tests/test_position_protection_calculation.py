"""Tests for the position protection calculation functionality.

This module contains unit tests for the calculation methods of PositionProtection class.
"""
import pytest
from typing import Dict
from core.position_protection import PositionProtection, ProtectionLevels
from .test_position_protection_base import (
    protection,
    sample_position,
    sample_market_data
)

def test_calculate_dynamic_stops(protection: PositionProtection) -> None:
    """
    Test dynamic stop loss calculation.
    
    Args:
        protection: PositionProtection instance
        
    Verifies:
        - Stop levels relationship
        - Volatility impact on stops
    """
    entry_price = 40000.0
    current_price = 41000.0
    volatility = 0.15
    
    stop_loss, warning_level = protection.calculate_dynamic_stops(
        entry_price,
        current_price,
        volatility
    )
    
    # Verify stop loss is below entry and warning
    assert stop_loss < warning_level < current_price
    
    # Test with high volatility
    high_volatility = 0.3
    high_stop, high_warning = protection.calculate_dynamic_stops(
        entry_price,
        current_price,
        high_volatility
    )
    
    # Higher volatility should result in wider stops
    assert high_stop < stop_loss
    assert high_warning < warning_level

def test_calculate_profit_targets(protection: PositionProtection) -> None:
    """
    Test profit target calculation.
    
    Args:
        protection: PositionProtection instance
        
    Verifies:
        - Profit targets relationship
        - Market trend impact
    """
    entry_price = 40000.0
    stop_loss = 38000.0
    market_trend = 0.05
    
    take_profit, trailing_stop = protection.calculate_profit_targets(
        entry_price,
        stop_loss,
        market_trend
    )
    
    # Verify profit targets are above entry
    assert take_profit > entry_price
    assert trailing_stop > entry_price
    assert trailing_stop < take_profit
    
    # Test with strong uptrend
    strong_trend = 0.2
    trend_take_profit, trend_trailing = protection.calculate_profit_targets(
        entry_price,
        stop_loss,
        strong_trend
    )
    
    # Strong trend should result in higher targets
    assert trend_take_profit > take_profit
    assert trend_trailing > trailing_stop

def test_calculate_scaling_levels(protection: PositionProtection) -> None:
    """
    Test position scaling levels calculation.
    
    Args:
        protection: PositionProtection instance
        
    Verifies:
        - Scaling levels structure
        - Price and size relationships
    """
    entry_price = 40000.0
    position_size = 1.0
    volatility = 0.15
    
    scaling_levels = protection.calculate_scaling_levels(
        entry_price,
        position_size,
        volatility
    )
    
    # Verify structure and values
    assert 'scale_out_1' in scaling_levels
    assert 'scale_in_1' in scaling_levels
    assert len(scaling_levels) == protection._config['scale_out_steps'] * 2
    
    # Verify scaling prices
    assert scaling_levels['scale_out_1']['price'] > entry_price
    assert scaling_levels['scale_in_1']['price'] < entry_price
    
    # Verify scaling sizes
    expected_size = position_size * protection._config['scale_ratio']
    assert scaling_levels['scale_out_1']['size'] == expected_size
    assert scaling_levels['scale_in_1']['size'] == expected_size

def test_get_protection_levels(
    protection: PositionProtection,
    sample_position: Dict[str, float],
    sample_market_data: Dict[str, float]
) -> None:
    """
    Test complete protection levels calculation.
    
    Args:
        protection: PositionProtection instance
        sample_position: Sample position data
        sample_market_data: Sample market data
        
    Verifies:
        - Return type
        - Level relationships
    """
    levels = protection.get_protection_levels(sample_position, sample_market_data)
    
    # Verify return type
    assert isinstance(levels, ProtectionLevels)
    
    # Verify logical relationships
    assert levels.stop_loss < levels.warning_level
    assert levels.warning_level < sample_position['entry_price']
    assert levels.take_profit > sample_position['entry_price']
    assert levels.trailing_stop < levels.take_profit
    assert levels.scale_in_level < levels.scale_out_level

def test_protection_with_minimal_market_data(protection: PositionProtection) -> None:
    """
    Test protection calculation with minimal market data.
    
    Args:
        protection: PositionProtection instance
        
    Verifies:
        - Handling of missing market data
        - Basic level calculations
    """
    position = {'entry_price': 40000.0, 'size': 1.0}
    market_data = {'price': 41000.0}
    
    levels = protection.get_protection_levels(position, market_data)
    
    # Verify protection levels are still calculated
    assert isinstance(levels, ProtectionLevels)
    assert levels.stop_loss > 0
    assert levels.take_profit > levels.stop_loss