"""
Nervous System Module - Real-time market data acquisition and processing.

This module implements the nervous system component responsible for:
1. Real-time data streaming and processing
2. Pattern recognition and technical analysis
3. Signal generation and filtering
4. Performance monitoring and optimization
"""
from typing import Dict, List, Optional, Tuple, Generator
import logging
import time
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from utils.config import ConfigManager
from utils.logger_base import get_logger
from core.exceptions import NervousSystemError

logger = get_logger(__name__)

@dataclass
class MarketData:
    """Container for market data points."""
    timestamp: datetime
    price: float
    volume: float
    trades: List[Dict]
    orderbook: Dict[str, List[Tuple[float, float]]]
    
    def validate(self) -> bool:
        """Validate data point integrity."""
        try:
            if not all([self.timestamp, self.price > 0, self.volume >= 0]):
                return False
            if not self.orderbook.get('bids') or not self.orderbook.get('asks'):
                return False
            return True
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return False

class NervousMetrics:
    """Performance metrics tracking for the nervous system."""
    
    def __init__(self):
        self.metrics = {
            'data_quality': {
                'value': 0.0,
                'description': 'Qualità dei dati acquisiti',
                'calculation': 'valid_datapoints / total_datapoints',
                'optimal_range': '> 0.99',
                'update_frequency': 'Real-time'
            },
            'processing_latency': {
                'value': 0.0,
                'description': 'Latenza elaborazione dati',
                'calculation': 'time_received - time_processed',
                'optimal_range': '< 10ms',
                'update_frequency': 'Per evento'
            },
            'pattern_detection': {
                'value': 0.0,
                'description': 'Accuratezza rilevamento pattern',
                'calculation': 'correct_patterns / total_patterns',
                'optimal_range': '> 0.85',
                'update_frequency': 'Per pattern'
            },
            'signal_noise_ratio': {
                'value': 0.0,
                'description': 'Rapporto segnale/rumore',
                'calculation': 'signal_strength / noise_level',
                'optimal_range': '> 3.0',
                'update_frequency': 'Continuous'
            },
            'data_throughput': {
                'value': 0.0,
                'description': 'Capacità elaborazione dati',
                'calculation': 'processed_events / second',
                'optimal_range': '> 1000',
                'update_frequency': 'Real-time'
            }
        }
        
    def update_metric(self, metric_name: str, value: float) -> None:
        """Update a specific metric value."""
        if metric_name not in self.metrics:
            raise NervousSystemError(f"Invalid metric name: {metric_name}")
        self.metrics[metric_name]['value'] = value
        
    def get_system_health(self) -> float:
        """Calculate overall system health score."""
        if not self.metrics:
            return 0.0
        
        total = sum(metric['value'] for metric in self.metrics.values())
        return total / len(self.metrics)

class PaperDataStreamer:
    """Simulated market data streaming for paper trading."""
    
    def __init__(self, config: Dict):
        """Initialize paper trading data streamer."""
        self.config = config
        self.current_timeframe = config['paper_trading']['default_timeframe']
        self.simulation_speed = config['paper_trading']['simulation_speed']
        self.pairs = config['paper_trading']['pairs']
        self.buffer_size = config['paper_trading']['buffer_size']
        
        # Initialize data buffers
        self.data_buffers = {
            pair['symbol']: [] for pair in self.pairs
        }
        
    def set_timeframe(self, timeframe: str) -> None:
        """Set the streaming timeframe."""
        if timeframe not in self.config['paper_trading']['timeframes']:
            raise NervousSystemError(f"Invalid timeframe: {timeframe}")
        self.current_timeframe = timeframe
        logger.info(f"Timeframe set to {timeframe}")
        
    def set_simulation_speed(self, speed: float) -> None:
        """Set the simulation speed multiplier."""
        if speed <= 0:
            raise NervousSystemError("Simulation speed must be positive")
        self.simulation_speed = speed
        logger.info(f"Simulation speed set to {speed}x")
        
    def generate_market_data(self, symbol: str) -> MarketData:
        """Generate simulated market data for a symbol."""
        pair_config = next(p for p in self.pairs if p['symbol'] == symbol)
        
        # Generate simulated price within configured range
        prev_price = self.data_buffers[symbol][-1].price if self.data_buffers[symbol] else pair_config['min_price']
        max_change = (pair_config['max_price'] - pair_config['min_price']) * 0.001  # Max 0.1% change
        price_change = random.uniform(-max_change, max_change)
        new_price = max(min(prev_price + price_change, pair_config['max_price']), pair_config['min_price'])
        
        # Generate simulated volume
        volume = random.uniform(100, 1000)
        
        # Generate simulated trades
        num_trades = random.randint(1, 5)
        trades = [
            {
                'id': i,
                'price': new_price + random.uniform(-0.1, 0.1),
                'volume': volume / num_trades
            }
            for i in range(num_trades)
        ]
        
        # Generate simulated orderbook
        spread = new_price * 0.0002  # 0.02% spread
        orderbook = {
            'bids': [
                (new_price - spread * (i+1), random.uniform(100, 1000))
                for i in range(5)
            ],
            'asks': [
                (new_price + spread * (i+1), random.uniform(100, 1000))
                for i in range(5)
            ]
        }
        
        return MarketData(
            timestamp=datetime.now(),
            price=new_price,
            volume=volume,
            trades=trades,
            orderbook=orderbook
        )
    
    def stream_data(self, symbol: str) -> Generator[MarketData, None, None]:
        """Stream simulated market data."""
        while True:
            data = self.generate_market_data(symbol)
            
            # Update buffer
            self.data_buffers[symbol].append(data)
            if len(self.data_buffers[symbol]) > self.buffer_size:
                self.data_buffers[symbol].pop(0)
                
            # Calculate sleep time based on timeframe and speed
            timeframe_seconds = {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '1h': 3600,
                '4h': 14400,
                '1d': 86400
            }[self.current_timeframe]
            
            sleep_time = timeframe_seconds / self.simulation_speed
            time.sleep(sleep_time)
            
            yield data

class NervousSystem:
    """Main nervous system class for market data processing."""
    
    def __init__(self):
        """Initialize the nervous system with configuration."""
        self.config = ConfigManager().get_config('nervous')
        self.metrics = NervousMetrics()
        self.streamer = PaperDataStreamer(self.config)
        self._initialize_components()
        
    def _initialize_components(self) -> None:
        """Initialize system components and connections."""
        try:
            # Initialize websocket connection parameters
            self.ws_params = self.config.get('websocket', {})
            
            # Initialize preprocessing parameters
            self.preprocessing_params = self.config.get('preprocessing', {
                'outlier_threshold': 3.0,
                'smoothing_window': 5,
                'aggregation_period': '1m'
            })
            
            # Initialize pattern recognition parameters
            self.pattern_params = self.config.get('patterns', {
                'min_confidence': 0.85,
                'lookback_period': 100,
                'validation_threshold': 0.75
            })
            
            logger.info("Nervous system components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize nervous system: {e}")
            raise NervousSystemError(f"Initialization failed: {e}")
    
    def set_timeframe(self, timeframe: str) -> None:
        """Set the data streaming timeframe."""
        self.streamer.set_timeframe(timeframe)
        
    def set_simulation_speed(self, speed: float) -> None:
        """Set the simulation speed."""
        self.streamer.set_simulation_speed(speed)
    
    def process_market_data(self, data: MarketData) -> Dict:
        """Process incoming market data and generate signals."""
        if not data.validate():
            logger.warning("Invalid market data received")
            return {'status': 'error', 'message': 'Invalid data'}
            
        try:
            # Preprocess data
            processed_data = self._preprocess_data(data)
            
            # Detect patterns
            patterns = self._detect_patterns(processed_data)
            
            # Generate signals
            signals = self._generate_signals(patterns)
            
            # Update metrics
            self._update_processing_metrics(data)
            
            return {
                'status': 'success',
                'signals': signals,
                'patterns': patterns,
                'metrics': {
                    name: metric['value'] 
                    for name, metric in self.metrics.metrics.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def start_streaming(self, symbol: str) -> Generator[Dict, None, None]:
        """Start streaming and processing market data."""
        logger.info(f"Starting data stream for {symbol}")
        try:
            for data in self.streamer.stream_data(symbol):
                result = self.process_market_data(data)
                yield result
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise NervousSystemError(f"Streaming failed: {e}")
    
    def _preprocess_data(self, data: MarketData) -> Dict:
        """Preprocess raw market data."""
        # Implementation details to be added
        return {}
    
    def _detect_patterns(self, data: Dict) -> List[Dict]:
        """Detect patterns in preprocessed data."""
        # Implementation details to be added
        return []
    
    def _generate_signals(self, patterns: List[Dict]) -> List[Dict]:
        """Generate trading signals from detected patterns."""
        # Implementation details to be added
        return []
    
    def _update_processing_metrics(self, data: MarketData) -> None:
        """Update processing metrics after data handling."""
        # Implementation details to be added
        pass
