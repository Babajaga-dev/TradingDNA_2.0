"""Test suite for Position Sizer module."""
import pytest
from decimal import Decimal
from dataclasses import dataclass
from core.metabolism.position_sizer import PositionSizer, PositionConfig

@pytest.fixture
def position_config():
    """Create position config for testing."""
    return PositionConfig(
        max_position_size=Decimal('1000'),
        risk_per_trade=0.01,
        stop_loss_pct=0.02,
        max_exposure_pct=0.8
    )

@pytest.fixture
def position_sizer(position_config):
    """Create position sizer instance for testing."""
    return PositionSizer(position_config)

def test_position_config_validation():
    """Test position config validation."""
    # Valid config
    config = PositionConfig(
        max_position_size=Decimal('1000'),
        risk_per_trade=0.01,
        stop_loss_pct=0.02,
        max_exposure_pct=0.8
    )
    sizer = PositionSizer(config)
    assert sizer is not None

    # Invalid max position size
    with pytest.raises(ValueError):
        PositionConfig(
            max_position_size=Decimal('-1000'),
            risk_per_trade=0.01,
            stop_loss_pct=0.02,
            max_exposure_pct=0.8
        )

    # Invalid risk percentage
    with pytest.raises(ValueError):
        PositionConfig(
            max_position_size=Decimal('1000'),
            risk_per_trade=1.5,
            stop_loss_pct=0.02,
            max_exposure_pct=0.8
        )

def test_calculate_position_size(position_sizer):
    """Test position size calculation."""
    capital = Decimal('10000')
    entry_price = Decimal('100')
    stop_loss = Decimal('98')

    # Test with stop loss price
    size, metrics = position_sizer.calculate_position_size(
        capital=capital,
        entry_price=entry_price,
        stop_loss=stop_loss
    )
    assert size > Decimal('0')
    assert size <= position_sizer._config.max_position_size
    assert 'risk_amount' in metrics
    assert 'final_size' in metrics

    # Test with signal strength adjustment
    size_strong, metrics_strong = position_sizer.calculate_position_size(
        capital=capital,
        entry_price=entry_price,
        stop_loss=stop_loss,
        signal_strength=0.8
    )
    assert size_strong < size  # Lower signal strength = smaller position

def test_position_limits(position_sizer):
    """Test position size limits."""
    capital = Decimal('100000')
    entry_price = Decimal('100')

    # Test max position size limit
    size, _ = position_sizer.calculate_position_size(
        capital=capital,
        entry_price=entry_price
    )
    assert size <= position_sizer._config.max_position_size

    # Test capital limit
    small_capital = Decimal('500')
    size_small, _ = position_sizer.calculate_position_size(
        capital=small_capital,
        entry_price=entry_price
    )
    assert size_small <= small_capital / entry_price

def test_exposure_management(position_sizer):
    """Test exposure management."""
    capital = Decimal('10000')
    entry_price = Decimal('100')

    # Test opening position within limits
    assert position_sizer.can_open_position('pos1', Decimal('50'), capital)
    position_sizer.open_position('pos1', Decimal('50'))

    # Test exposure tracking
    assert position_sizer.get_total_exposure() == Decimal('50')
    assert 'pos1' in position_sizer.get_position_exposure()

    # Test max exposure limit
    max_allowed = capital * Decimal(str(position_sizer._config.max_exposure_pct))
    assert not position_sizer.can_open_position('pos2', max_allowed + Decimal('1'), capital)

def test_position_lifecycle(position_sizer):
    """Test complete position lifecycle."""
    # Open position
    assert position_sizer.open_position('pos1', Decimal('100'))
    assert position_sizer.get_total_exposure() == Decimal('100')

    # Update position
    result = position_sizer.update_position_size('pos1', Decimal('150'))
    assert result is not None
    old_size, new_size = result
    assert old_size == Decimal('100')
    assert new_size == Decimal('150')
    assert position_sizer.get_total_exposure() == Decimal('150')

    # Close position
    closed_size = position_sizer.close_position('pos1')
    assert closed_size == Decimal('150')
    assert position_sizer.get_total_exposure() == Decimal('0')

def test_multiple_positions(position_sizer):
    """Test handling multiple positions."""
    # Open multiple positions
    position_sizer.open_position('pos1', Decimal('100'))
    position_sizer.open_position('pos2', Decimal('150'))
    position_sizer.open_position('pos3', Decimal('200'))

    # Verify total exposure
    assert position_sizer.get_total_exposure() == Decimal('450')

    # Verify individual positions
    exposures = position_sizer.get_position_exposure()
    assert exposures['pos1'] == Decimal('100')
    assert exposures['pos2'] == Decimal('150')
    assert exposures['pos3'] == Decimal('200')

def test_invalid_operations(position_sizer):
    """Test handling of invalid operations."""
    # Test duplicate position
    position_sizer.open_position('pos1', Decimal('100'))
    assert not position_sizer.open_position('pos1', Decimal('150'))

    # Test updating non-existent position
    assert position_sizer.update_position_size('non_existent', Decimal('100')) is None

    # Test closing non-existent position
    assert position_sizer.close_position('non_existent') is None

def test_risk_based_sizing(position_sizer):
    """Test risk-based position sizing."""
    capital = Decimal('10000')
    entry_price = Decimal('100')
    stop_loss = Decimal('95')  # 5% stop loss

    # Calculate size based on risk
    size, metrics = position_sizer.calculate_position_size(
        capital=capital,
        entry_price=entry_price,
        stop_loss=stop_loss
    )

    # Verify risk amount
    risk_amount = metrics['risk_amount']
    assert risk_amount == capital * Decimal(str(position_sizer._config.risk_per_trade))

    # Verify position size respects risk limit
    max_loss = (entry_price - stop_loss) * size
    assert max_loss <= risk_amount

def test_signal_strength_impact(position_sizer):
    """Test impact of signal strength on position sizing."""
    capital = Decimal('10000')
    entry_price = Decimal('100')

    # Test various signal strengths
    sizes = []
    for strength in [0.2, 0.5, 0.8, 1.0]:
        size, _ = position_sizer.calculate_position_size(
            capital=capital,
            entry_price=entry_price,
            signal_strength=strength
        )
        sizes.append(size)

    # Verify sizes increase with signal strength
    assert all(sizes[i] <= sizes[i+1] for i in range(len(sizes)-1))
