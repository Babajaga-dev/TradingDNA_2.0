"""Test module for the Nervous System component."""
import pytest
from datetime import datetime
from typing import Dict, List
import time

from core.nervous_system import (
    NervousSystem, 
    MarketData, 
    NervousMetrics,
    PaperDataStreamer
)
from core.exceptions import NervousSystemError
from utils.config import ConfigManager

@pytest.fixture
def config():
    """Get nervous system configuration."""
    return ConfigManager().get_config('nervous')

@pytest.fixture
def nervous_system():
    """Create a NervousSystem instance for testing."""
    return NervousSystem()

@pytest.fixture
def market_data():
    """Create sample market data for testing."""
    return MarketData(
        timestamp=datetime.now(),
        price=100.0,
        volume=1000.0,
        trades=[
            {'id': 1, 'price': 100.0, 'volume': 500.0},
            {'id': 2, 'price': 100.0, 'volume': 500.0}
        ],
        orderbook={
            'bids': [(99.9, 1000.0), (99.8, 2000.0)],
            'asks': [(100.1, 1000.0), (100.2, 2000.0)]
        }
    )

@pytest.fixture
def metrics():
    """Create NervousMetrics instance for testing."""
    return NervousMetrics()

@pytest.fixture
def paper_streamer(config):
    """Create PaperDataStreamer instance for testing."""
    return PaperDataStreamer(config)

def test_nervous_system_initialization(nervous_system):
    """Test nervous system initialization."""
    assert nervous_system is not None
    assert nervous_system.config is not None
    assert nervous_system.metrics is not None
    assert nervous_system.streamer is not None
    assert hasattr(nervous_system, 'ws_params')
    assert hasattr(nervous_system, 'preprocessing_params')
    assert hasattr(nervous_system, 'pattern_params')

def test_market_data_validation(market_data):
    """Test market data validation."""
    assert market_data.validate() is True
    
    # Test invalid data
    invalid_data = MarketData(
        timestamp=None,
        price=-100.0,
        volume=-1000.0,
        trades=[],
        orderbook={'bids': [], 'asks': []}
    )
    assert invalid_data.validate() is False

def test_metrics_initialization(metrics):
    """Test metrics initialization."""
    expected_metrics = [
        'data_quality',
        'processing_latency',
        'pattern_detection',
        'signal_noise_ratio',
        'data_throughput'
    ]
    
    for metric in expected_metrics:
        assert metric in metrics.metrics
        assert metrics.metrics[metric]['value'] == 0.0
        assert 'description' in metrics.metrics[metric]
        assert 'calculation' in metrics.metrics[metric]
        assert 'optimal_range' in metrics.metrics[metric]
        assert 'update_frequency' in metrics.metrics[metric]

def test_metrics_update(metrics):
    """Test metrics update functionality."""
    metrics.update_metric('data_quality', 0.95)
    assert metrics.metrics['data_quality']['value'] == 0.95
    
    with pytest.raises(NervousSystemError):
        metrics.update_metric('invalid_metric', 1.0)

def test_system_health_calculation(metrics):
    """Test system health calculation."""
    # All metrics at 0
    assert metrics.get_system_health() == 0.0
    
    # Update all metrics
    test_values = {
        'data_quality': 0.99,
        'processing_latency': 0.95,
        'pattern_detection': 0.90,
        'signal_noise_ratio': 0.85,
        'data_throughput': 0.95
    }
    
    for metric, value in test_values.items():
        metrics.update_metric(metric, value)
    
    expected_health = sum(test_values.values()) / len(test_values)
    assert abs(metrics.get_system_health() - expected_health) < 0.001

def test_market_data_processing(nervous_system, market_data):
    """Test market data processing pipeline."""
    result = nervous_system.process_market_data(market_data)
    
    assert result['status'] == 'success'
    assert 'signals' in result
    assert 'patterns' in result
    assert 'metrics' in result
    
    # Test with invalid data
    invalid_data = MarketData(
        timestamp=None,
        price=-100.0,
        volume=-1000.0,
        trades=[],
        orderbook={'bids': [], 'asks': []}
    )
    result = nervous_system.process_market_data(invalid_data)
    assert result['status'] == 'error'
    assert 'message' in result

def test_configuration_loading():
    """Test configuration loading."""
    config = ConfigManager().get_config('nervous')
    
    required_sections = [
        'paper_trading',
        'websocket',
        'preprocessing',
        'patterns',
        'technical_analysis',
        'performance',
        'optimization',
        'logging'
    ]
    
    for section in required_sections:
        assert section in config

def test_error_handling(nervous_system):
    """Test error handling in various scenarios."""
    # Test initialization error
    with pytest.raises(NervousSystemError):
        nervous_system._initialize_components = lambda: exec('raise NervousSystemError("Test error")')
        nervous_system.__init__()

def test_preprocessing(nervous_system, market_data):
    """Test data preprocessing functionality."""
    processed_data = nervous_system._preprocess_data(market_data)
    assert isinstance(processed_data, dict)

def test_pattern_detection(nervous_system):
    """Test pattern detection functionality."""
    patterns = nervous_system._detect_patterns({})
    assert isinstance(patterns, list)

def test_signal_generation(nervous_system):
    """Test signal generation functionality."""
    signals = nervous_system._generate_signals([])
    assert isinstance(signals, list)

def test_metrics_update_processing(nervous_system, market_data):
    """Test metrics update during processing."""
    nervous_system._update_processing_metrics(market_data)
    assert nervous_system.metrics is not None

def test_paper_streamer_initialization(paper_streamer, config):
    """Test paper trading streamer initialization."""
    assert paper_streamer.current_timeframe == config['paper_trading']['default_timeframe']
    assert paper_streamer.simulation_speed == config['paper_trading']['simulation_speed']
    assert len(paper_streamer.pairs) == len(config['paper_trading']['pairs'])
    assert paper_streamer.buffer_size == config['paper_trading']['buffer_size']

def test_paper_streamer_timeframe(paper_streamer):
    """Test timeframe configuration."""
    # Test valid timeframe
    paper_streamer.set_timeframe('5m')
    assert paper_streamer.current_timeframe == '5m'
    
    # Test invalid timeframe
    with pytest.raises(NervousSystemError):
        paper_streamer.set_timeframe('invalid')

def test_paper_streamer_speed(paper_streamer):
    """Test simulation speed configuration."""
    # Test valid speed
    paper_streamer.set_simulation_speed(2.0)
    assert paper_streamer.simulation_speed == 2.0
    
    # Test invalid speed
    with pytest.raises(NervousSystemError):
        paper_streamer.set_simulation_speed(0)
    with pytest.raises(NervousSystemError):
        paper_streamer.set_simulation_speed(-1)

def test_market_data_generation(paper_streamer):
    """Test market data generation."""
    symbol = paper_streamer.pairs[0]['symbol']
    data = paper_streamer.generate_market_data(symbol)
    
    assert isinstance(data, MarketData)
    assert data.validate()
    assert paper_streamer.pairs[0]['min_price'] <= data.price <= paper_streamer.pairs[0]['max_price']
    assert data.volume > 0
    assert len(data.trades) > 0
    assert len(data.orderbook['bids']) > 0
    assert len(data.orderbook['asks']) > 0

def test_data_streaming(paper_streamer):
    """Test data streaming functionality."""
    symbol = paper_streamer.pairs[0]['symbol']
    
    # Set fast timeframe and speed for testing
    paper_streamer.set_timeframe('1m')
    paper_streamer.set_simulation_speed(60.0)  # 1 minute = 1 second
    
    # Get first few data points
    stream = paper_streamer.stream_data(symbol)
    data_points = []
    
    start_time = time.time()
    for _ in range(3):
        data = next(stream)
        data_points.append(data)
        assert isinstance(data, MarketData)
        assert data.validate()
    
    # Check timing
    elapsed = time.time() - start_time
    assert 2.8 <= elapsed <= 3.2  # ~3 seconds (3 points at 1 second each)
    
    # Check buffer
    assert len(paper_streamer.data_buffers[symbol]) <= paper_streamer.buffer_size
    assert len(data_points) == 3

def test_nervous_system_streaming(nervous_system):
    """Test nervous system streaming integration."""
    symbol = nervous_system.config['paper_trading']['pairs'][0]['symbol']
    
    # Set fast timeframe and speed for testing
    nervous_system.set_timeframe('1m')
    nervous_system.set_simulation_speed(60.0)
    
    # Get first few results
    stream = nervous_system.start_streaming(symbol)
    results = []
    
    start_time = time.time()
    for _ in range(3):
        result = next(stream)
        results.append(result)
        assert result['status'] == 'success'
        assert 'signals' in result
        assert 'patterns' in result
        assert 'metrics' in result
    
    # Check timing
    elapsed = time.time() - start_time
    assert 2.8 <= elapsed <= 3.2  # ~3 seconds