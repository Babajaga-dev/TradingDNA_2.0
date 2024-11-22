"""Tests for the immune system module."""
import pytest
from core.immune_system import ImmuneSystem, RiskMetrics, DefenseMetrics

@pytest.fixture
def immune_system():
    """Create a test instance of ImmuneSystem."""
    return ImmuneSystem()

@pytest.fixture
def sample_position():
    """Create a sample position for testing."""
    return {
        'symbol': 'BTC/USD',
        'size': 1.0,
        'entry_price': 40000.0,
        'current_price': 41000.0,
        'unrealized_pnl': 1000.0
    }

@pytest.fixture
def sample_market_data():
    """Create sample market data for testing."""
    return {
        'price': 41000.0,
        'volume': 100.0,
        'volatility': 0.15,
        'timestamp': 1644300000
    }

def test_immune_system_initialization(immune_system):
    """Test immune system initialization with default parameters."""
    assert isinstance(immune_system, ImmuneSystem)
    health = immune_system.get_system_health()
    assert 'risk_management' in health
    assert 'defense_efficiency' in health
    assert 'system_stability' in health

def test_analyze_risk(immune_system):
    """Test risk analysis functionality."""
    positions = [
        {
            'symbol': 'BTC/USD',
            'size': 1.0,
            'entry_price': 40000.0
        }
    ]
    risk_metrics = immune_system.analyze_risk(positions)
    assert isinstance(risk_metrics, RiskMetrics)
    assert hasattr(risk_metrics, 'total_exposure')
    assert hasattr(risk_metrics, 'drawdown')
    assert hasattr(risk_metrics, 'counterparty_risk')
    assert hasattr(risk_metrics, 'asset_correlation')

def test_dynamic_stops_calculation(immune_system, sample_position):
    """Test dynamic stop loss calculation."""
    volatility = 0.15
    stop_loss, take_profit = immune_system.calculate_dynamic_stops(
        sample_position,
        volatility
    )
    assert isinstance(stop_loss, float)
    assert isinstance(take_profit, float)
    assert stop_loss < sample_position['entry_price']
    assert take_profit > sample_position['entry_price']

def test_extreme_event_detection(immune_system, sample_market_data):
    """Test extreme market event detection."""
    result = immune_system.detect_extreme_events(sample_market_data)
    assert isinstance(result, bool)

def test_signal_filtering(immune_system):
    """Test trading signal filtering."""
    signal = {
        'symbol': 'BTC/USD',
        'type': 'LONG',
        'price': 41000.0,
        'confidence': 0.8
    }
    filtered_signal = immune_system.filter_signal(signal)
    assert filtered_signal is None or isinstance(filtered_signal, dict)

def test_metrics_update(immune_system):
    """Test metrics update functionality."""
    new_metrics = DefenseMetrics(
        false_positive_rate=0.05,
        reaction_time=45.0,
        protection_efficiency=0.95,
        system_stability=0.92
    )
    immune_system.update_metrics(new_metrics)
    health = immune_system.get_system_health()
    assert isinstance(health, dict)
    assert all(isinstance(v, float) for v in health.values())

def test_system_health_calculation(immune_system):
    """Test system health calculation."""
    health = immune_system.get_system_health()
    assert isinstance(health, dict)
    assert 'risk_management' in health
    assert 'defense_efficiency' in health
    assert 'system_stability' in health
    assert all(0.0 <= v <= 1.0 for v in health.values())
