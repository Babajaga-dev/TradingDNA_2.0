"""Tests for the position protection module.

This module imports and re-exports all position protection tests from specialized modules.
"""
# Import fixtures
from .test_position_protection_base import (
    protection,
    custom_protection,
    sample_position,
    sample_market_data
)

# Import base tests
from .test_position_protection_base import (
    test_protection_levels_dataclass,
    test_position_protection_initialization,
    test_custom_position_protection_initialization
)

# Import calculation tests
from .test_position_protection_calculation import (
    test_calculate_dynamic_stops,
    test_calculate_profit_targets,
    test_calculate_scaling_levels,
    test_get_protection_levels,
    test_protection_with_minimal_market_data
)

# Import adaptation tests
from .test_position_protection_adaptation import (
    test_adapt_to_market_conditions,
    test_protection_with_extreme_volatility,
    test_protection_with_strong_trend
)

__all__ = [
    # Fixtures
    'protection',
    'custom_protection',
    'sample_position',
    'sample_market_data',
    
    # Base tests
    'test_protection_levels_dataclass',
    'test_position_protection_initialization',
    'test_custom_position_protection_initialization',
    
    # Calculation tests
    'test_calculate_dynamic_stops',
    'test_calculate_profit_targets',
    'test_calculate_scaling_levels',
    'test_get_protection_levels',
    'test_protection_with_minimal_market_data',
    
    # Adaptation tests
    'test_adapt_to_market_conditions',
    'test_protection_with_extreme_volatility',
    'test_protection_with_strong_trend'
]