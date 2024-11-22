"""Tests for the immune system module."""
import pytest
from core.immune_system import ImmuneSystem, RiskMetrics, DefenseMetrics

@pytest.fixture
def immune_system():
    """Create a test instance of ImmuneSystem."""
    return ImmuneSystem()

@pytest.fixture
def sample_positions():
    """Create sample positions for testing."""
    return [
        {
            'symbol': 'BTC/USD',
            'size': 1.0,
            'entry_price': 40000.0,
            'current_price': 41000.0,
            'unrealized_pnl': 1000.0,
            'exchange': 'binance',
            'price_history': [39000.0, 39500.0, 40000.0, 40500.0, 41000.0]
        },
        {
            'symbol': 'ETH/USD',
            'size': 10.0,
            'entry_price': 2800.0,
            'current_price': 2900.0,
            'unrealized_pnl': 1000.0,
            'exchange': 'kraken',
            'price_history': [2700.0, 2750.0, 2800.0, 2850.0, 2900.0]
        }
    ]

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
    """Test immune system initialization."""
    assert immune_system._risk_manager is not None
    assert immune_system._metrics is not None
    assert immune_system._market_state is not None
    assert isinstance(immune_system._exchange_health, dict)

def test_analyze_risk(immune_system, sample_positions):
    """Test risk analysis functionality."""
    risk_metrics = immune_system.analyze_risk(sample_positions)
    assert isinstance(risk_metrics, RiskMetrics)
    assert 0 <= risk_metrics.total_exposure <= 1
    assert 0 <= risk_metrics.drawdown <= 1
    assert 0 <= risk_metrics.counterparty_risk <= 1
    assert 0 <= risk_metrics.asset_correlation <= 1

def test_calculate_dynamic_stops(immune_system, sample_positions):
    """Test dynamic stop loss calculation."""
    position = sample_positions[0]
    volatility = 0.15
    
    stop_loss, take_profit = immune_system.calculate_dynamic_stops(
        position,
        volatility
    )
    
    assert stop_loss < position['entry_price']
    assert take_profit > position['entry_price']
    assert stop_loss > 0
    assert take_profit > 0

def test_detect_extreme_events(immune_system, sample_market_data):
    """Test extreme event detection."""
    # Normal market conditions
    assert not immune_system.detect_extreme_events(sample_market_data)
    
    # Extreme price movement
    extreme_data = sample_market_data.copy()
    extreme_data['price'] = sample_market_data['price'] * 1.2
    assert immune_system.detect_extreme_events(extreme_data)
    
    # Extreme volume
    extreme_volume = sample_market_data.copy()
    extreme_volume['volume'] = sample_market_data['volume'] * 4
    assert immune_system.detect_extreme_events(extreme_volume)

def test_filter_signal(immune_system):
    """Test signal filtering."""
    # Valid signal
    valid_signal = {
        'type': 'LONG',
        'confidence': 0.8,
        'price': 40000.0
    }
    assert immune_system.filter_signal(valid_signal) is not None
    
    # Low confidence signal
    low_conf_signal = valid_signal.copy()
    low_conf_signal['confidence'] = 0.6
    assert immune_system.filter_signal(low_conf_signal) is None
    
    # High risk environment
    immune_system._market_state['risk_level'] = 'high'
    assert immune_system.filter_signal(valid_signal) is None

def test_get_system_health(immune_system):
    """Test system health monitoring."""
    health = immune_system.get_system_health()
    assert isinstance(health, dict)
    assert 'risk_management' in health
    assert 'defense_efficiency' in health
    assert 'system_stability' in health
    assert all(0 <= v <= 1 for v in health.values())

def test_update_metrics(immune_system):
    """Test metrics update functionality."""
    new_metrics = DefenseMetrics(
        false_positive_rate=0.1,
        reaction_time=0.2,
        protection_efficiency=0.9,
        system_stability=0.95
    )
    immune_system.update_metrics(new_metrics)
    assert immune_system._metrics == new_metrics

def test_assess_counterparty_risk(immune_system, sample_positions):
    """Test counterparty risk assessment."""
    # Test with default exchange health
    risk = immune_system._assess_counterparty_risk(sample_positions)
    assert isinstance(risk, float)
    assert 0 <= risk <= 1
    
    # Test with custom exchange health
    immune_system._exchange_health = {
        'binance': {
            'uptime': 0.99,
            'api_response_time': 100,
            'error_rate': 0.01
        },
        'kraken': {
            'uptime': 0.95,
            'api_response_time': 300,
            'error_rate': 0.05
        }
    }
    risk_with_health = immune_system._assess_counterparty_risk(sample_positions)
    assert isinstance(risk_with_health, float)
    assert 0 <= risk_with_health <= 1

def test_get_exchange_health_score(immune_system):
    """Test exchange health score calculation."""
    # Test unknown exchange
    unknown_score = immune_system._get_exchange_health_score('unknown')
    assert unknown_score == 0.8  # Default score
    
    # Test with health metrics
    immune_system._exchange_health['binance'] = {
        'uptime': 0.99,
        'api_response_time': 100,
        'error_rate': 0.01
    }
    score = immune_system._get_exchange_health_score('binance')
    assert isinstance(score, float)
    assert 0 <= score <= 1
    assert score > 0.8  # Should be better than default

def test_calculate_drawdown(immune_system, sample_positions):
    """Test drawdown calculation."""
    drawdown = immune_system._calculate_drawdown(sample_positions)
    assert isinstance(drawdown, float)
    assert 0 <= drawdown <= 1
    
    # Test with negative PnL
    negative_positions = sample_positions.copy()
    negative_positions[0]['unrealized_pnl'] = -2000.0
    negative_drawdown = immune_system._calculate_drawdown(negative_positions)
    assert negative_drawdown > 0

def test_empty_positions(immune_system):
    """Test handling of empty positions list."""
    risk_metrics = immune_system.analyze_risk([])
    assert risk_metrics.total_exposure == 0
    assert risk_metrics.drawdown == 0
    assert risk_metrics.counterparty_risk == 0
    assert risk_metrics.asset_correlation == 0

def test_market_state_update(immune_system, sample_market_data):
    """Test market state updates."""
    immune_system._update_market_state(sample_market_data)
    assert immune_system._market_state['price'] == sample_market_data['price']
    assert immune_system._market_state['volume'] == sample_market_data['volume']
    assert immune_system._market_state['volatility'] == sample_market_data['volatility']
    
    # Test price history tracking
    new_data = sample_market_data.copy()
    new_data['price'] = 42000.0
    immune_system._update_market_state(new_data)
    assert immune_system._market_state['previous_price'] == sample_market_data['price']
    assert immune_system._market_state['price'] == new_data['price']
