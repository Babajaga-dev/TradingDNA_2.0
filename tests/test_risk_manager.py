"""Tests for the risk manager module."""
import pytest
import numpy as np
from core.risk_manager import RiskManager, PositionRisk

@pytest.fixture
def risk_manager():
    """Create a test instance of RiskManager."""
    return RiskManager()

@pytest.fixture
def sample_position():
    """Create a sample position for testing."""
    return {
        'symbol': 'BTC/USD',
        'size': 1.0,
        'entry_price': 40000.0,
        'current_price': 41000.0,
        'unrealized_pnl': 1000.0,
        'price_history': [
            39000.0, 39500.0, 40000.0, 40500.0, 41000.0
        ]
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

@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio for testing."""
    return {
        'total_value': 100000.0,
        'positions': [
            {
                'symbol': 'BTC/USD',
                'size': 1.0,
                'entry_price': 40000.0,
                'current_price': 41000.0,
                'price_history': [
                    39000.0, 39500.0, 40000.0, 40500.0, 41000.0
                ]
            },
            {
                'symbol': 'ETH/USD',
                'size': 10.0,
                'entry_price': 2800.0,
                'current_price': 2900.0,
                'price_history': [
                    2700.0, 2750.0, 2800.0, 2850.0, 2900.0
                ]
            }
        ]
    }

def test_risk_manager_initialization(risk_manager):
    """Test risk manager initialization with default config."""
    assert isinstance(risk_manager, RiskManager)
    assert hasattr(risk_manager, '_config')
    assert 'max_position_size' in risk_manager._config
    assert 'max_total_exposure' in risk_manager._config
    assert 'var_confidence' in risk_manager._config
    assert 'position_size_fixed' in risk_manager._config

def test_calculate_position_risk(
    risk_manager,
    sample_position,
    sample_market_data,
    sample_portfolio
):
    """Test position risk calculation."""
    risk = risk_manager.calculate_position_risk(
        sample_position,
        sample_market_data,
        sample_portfolio
    )
    assert isinstance(risk, PositionRisk)
    assert 0 <= risk.total_risk <= 1
    assert 0 <= risk.exposure <= 1
    assert 0 <= risk.volatility_risk <= 1
    assert 0 <= risk.correlation_risk <= 1
    assert 0 <= risk.var_risk <= 1

def test_calculate_position_size(risk_manager, sample_market_data):
    """Test position size calculation."""
    available_capital = 100000.0
    size = risk_manager.calculate_position_size(
        available_capital,
        sample_market_data
    )
    assert isinstance(size, float)
    assert size > 0
    assert size <= available_capital * risk_manager._config['max_position_size']

def test_check_risk_limits(
    risk_manager,
    sample_position,
    sample_market_data,
    sample_portfolio
):
    """Test risk limits checking."""
    risk = risk_manager.calculate_position_risk(
        sample_position,
        sample_market_data,
        sample_portfolio
    )
    result = risk_manager.check_risk_limits(risk, sample_portfolio)
    assert isinstance(result, bool)

def test_calculate_drawdown_protection(
    risk_manager,
    sample_position,
    sample_market_data
):
    """Test drawdown protection calculation."""
    protection = risk_manager.calculate_drawdown_protection(
        sample_position,
        sample_market_data
    )
    assert isinstance(protection, dict)
    assert 'stop_loss' in protection
    assert 'warning_level' in protection
    assert 'risk_level' in protection
    assert protection['stop_loss'] < sample_position['entry_price']
    assert protection['warning_level'] < sample_position['entry_price']

def test_exposure_calculation(risk_manager, sample_position, sample_portfolio):
    """Test position exposure calculation."""
    exposure = risk_manager._calculate_exposure(sample_position, sample_portfolio)
    assert isinstance(exposure, float)
    assert 0 <= exposure <= 1

def test_volatility_risk_calculation(
    risk_manager,
    sample_position,
    sample_market_data
):
    """Test volatility risk calculation."""
    vol_risk = risk_manager._calculate_volatility_risk(
        sample_position,
        sample_market_data
    )
    assert isinstance(vol_risk, float)
    assert vol_risk > 0

def test_correlation_risk_calculation(risk_manager, sample_position, sample_portfolio):
    """Test correlation risk calculation."""
    corr_risk = risk_manager._calculate_correlation_risk(
        sample_position,
        sample_portfolio
    )
    assert isinstance(corr_risk, float)
    assert 0 <= corr_risk <= 1

def test_var_risk_calculation(risk_manager, sample_position, sample_market_data):
    """Test Value at Risk calculation."""
    var_risk = risk_manager._calculate_var_risk(
        sample_position,
        sample_market_data
    )
    assert isinstance(var_risk, float)
    assert 0 <= var_risk <= 1

def test_total_exposure_calculation(risk_manager, sample_portfolio):
    """Test total portfolio exposure calculation."""
    total_exposure = risk_manager._calculate_total_exposure(sample_portfolio)
    assert isinstance(total_exposure, float)
    assert 0 <= total_exposure <= 1

def test_risk_aggregation(risk_manager):
    """Test risk metrics aggregation."""
    exposure = 0.3
    volatility_risk = 0.2
    correlation_risk = 0.1
    var_risk = 0.15
    
    total_risk = risk_manager._aggregate_risk_metrics(
        exposure,
        volatility_risk,
        correlation_risk,
        var_risk
    )
    assert isinstance(total_risk, float)
    assert 0 <= total_risk <= 1

def test_custom_config():
    """Test risk manager with custom configuration."""
    custom_config = {
        'max_position_size': 0.05,
        'max_total_exposure': 0.15,
        'correlation_threshold': 0.6,
        'max_drawdown': 0.08,
        'volatility_multiplier': 1.5,
        'var_confidence': 0.99,
        'position_size_fixed': 0.01
    }
    risk_manager = RiskManager(config=custom_config)
    assert risk_manager._config == custom_config

def test_correlation_risk_with_insufficient_data(risk_manager, sample_position):
    """Test correlation risk calculation with insufficient data."""
    portfolio = {
        'total_value': 100000.0,
        'positions': [
            {
                'symbol': 'ETH/USD',
                'size': 10.0,
                'entry_price': 2800.0,
                'current_price': 2900.0,
                'price_history': []  # Empty history
            }
        ]
    }
    corr_risk = risk_manager._calculate_correlation_risk(sample_position, portfolio)
    assert corr_risk == 0.0

def test_var_risk_with_insufficient_data(risk_manager, sample_market_data):
    """Test VaR calculation with insufficient data."""
    position = {
        'symbol': 'BTC/USD',
        'size': 1.0,
        'entry_price': 40000.0,
        'current_price': 41000.0,
        'price_history': []  # Empty history
    }
    var_risk = risk_manager._calculate_var_risk(position, sample_market_data)
    assert var_risk == 0.0

def test_position_size_with_high_volatility(risk_manager):
    """Test position size calculation with high volatility."""
    market_data = {
        'price': 41000.0,
        'volatility': 0.5  # High volatility
    }
    size = risk_manager.calculate_position_size(100000.0, market_data)
    normal_size = risk_manager.calculate_position_size(
        100000.0,
        {'price': 41000.0, 'volatility': 0.1}
    )
    assert size < normal_size  # High volatility should reduce position size
