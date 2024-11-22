"""Tests for the position protection module.

This module contains unit tests for the PositionProtection class and related components,
verifying the correct implementation of position protection mechanisms including
dynamic stops, profit targets, and position scaling.
"""
from typing import Dict, Any
import pytest
from core.position_protection import PositionProtection, ProtectionLevels

@pytest.fixture
def protection() -> PositionProtection:
    """
    Create a test instance of PositionProtection with default configuration.
    
    Returns:
        PositionProtection: Instance with default config
    """
    return PositionProtection()

@pytest.fixture
def custom_protection() -> PositionProtection:
    """
    Create a test instance of PositionProtection with custom configuration.
    
    Returns:
        PositionProtection: Instance with custom config
    """
    config: Dict[str, Any] = {
        'volatility_multiplier': 1.5,
        'profit_take_multiplier': 2.0,
        'trailing_stop_activation': 0.6,
        'position_scale_threshold': 0.2,
        'market_trend_threshold': 0.15,
        'min_profit_target': 0.03,
        'max_stop_distance': 0.04,
        'scale_out_steps': 4,
        'scale_ratio': 0.2
    }
    return PositionProtection(config=config)

@pytest.fixture
def sample_position() -> Dict[str, float]:
    """
    Create a sample position for testing.
    
    Returns:
        Dict[str, float]: Sample position data
    """
    return {
        'entry_price': 40000.0,
        'size': 1.0,
        'current_price': 41000.0
    }

@pytest.fixture
def sample_market_data() -> Dict[str, float]:
    """
    Create sample market data for testing.
    
    Returns:
        Dict[str, float]: Sample market data
    """
    return {
        'price': 41000.0,
        'volatility': 0.15,
        'trend': 0.05,
        'volume': 1000.0
    }

def test_protection_levels_dataclass() -> None:
    """
    Test ProtectionLevels dataclass structure and relationships.
    
    Verifies:
        - Correct type for all fields
        - Logical relationships between levels
    """
    levels = ProtectionLevels(
        stop_loss=38000.0,
        warning_level=38500.0,
        take_profit=42000.0,
        trailing_stop=41000.0,
        scale_out_level=41500.0,
        scale_in_level=39000.0
    )
    
    assert isinstance(levels.stop_loss, float)
    assert isinstance(levels.warning_level, float)
    assert isinstance(levels.take_profit, float)
    assert isinstance(levels.trailing_stop, float)
    assert isinstance(levels.scale_out_level, float)
    assert isinstance(levels.scale_in_level, float)
    
    # Verify logical relationships
    assert levels.stop_loss < levels.warning_level
    assert levels.warning_level < levels.take_profit
    assert levels.trailing_stop <= levels.take_profit
    assert levels.scale_in_level < levels.scale_out_level

def test_position_protection_initialization(protection: PositionProtection) -> None:
    """
    Test position protection initialization with default config.
    
    Args:
        protection: Default configured PositionProtection instance
        
    Verifies:
        - Instance type
        - Default config values
    """
    assert isinstance(protection, PositionProtection)
    assert protection._config['volatility_multiplier'] == 2.0
    assert protection._config['profit_take_multiplier'] == 1.5
    assert protection._config['trailing_stop_activation'] == 0.5
    assert protection._config['position_scale_threshold'] == 0.3
    assert protection._config['market_trend_threshold'] == 0.1
    assert protection._config['min_profit_target'] == 0.02
    assert protection._config['max_stop_distance'] == 0.05
    assert protection._config['scale_out_steps'] == 3
    assert protection._config['scale_ratio'] == 0.25

def test_custom_position_protection_initialization(custom_protection: PositionProtection) -> None:
    """
    Test position protection initialization with custom config.
    
    Args:
        custom_protection: Custom configured PositionProtection instance
        
    Verifies:
        - Custom config values are correctly set
    """
    assert custom_protection._config['volatility_multiplier'] == 1.5
    assert custom_protection._config['profit_take_multiplier'] == 2.0
    assert custom_protection._config['trailing_stop_activation'] == 0.6
    assert custom_protection._config['position_scale_threshold'] == 0.2
    assert custom_protection._config['market_trend_threshold'] == 0.15
    assert custom_protection._config['min_profit_target'] == 0.03
    assert custom_protection._config['max_stop_distance'] == 0.04
    assert custom_protection._config['scale_out_steps'] == 4
    assert custom_protection._config['scale_ratio'] == 0.2

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
