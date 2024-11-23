"""Tests for the position protection module base functionality.

This module contains base unit tests for the PositionProtection class,
including fixtures and initialization tests.
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