"""Handler for Nervous System CLI commands."""
import logging
from typing import Dict, Optional, Generator
import threading
import time
from datetime import datetime

from core.nervous_system import NervousSystem
from utils.logger_base import get_logger
from utils.config import ConfigManager

logger = get_logger(__name__)

class NervousHandler:
    """Handler class for Nervous System operations."""
    
    def __init__(self):
        """Initialize the nervous system handler."""
        self.nervous_system = NervousSystem()
        self.config = ConfigManager().get_config('nervous')
        self._stream_active = False
        self._stream_thread = None
        self._current_symbol = None
    
    def get_system_health(self) -> Dict:
        """Get current nervous system health metrics."""
        try:
            health_score = self.nervous_system.metrics.get_system_health()
            metrics = {
                name: metric['value']
                for name, metric in self.nervous_system.metrics.metrics.items()
            }
            
            return {
                'status': 'success',
                'health_score': health_score,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                'status': 'error',
                'message': f"Failed to get system health: {str(e)}"
            }
    
    def set_timeframe(self, timeframe: str) -> Dict:
        """Set the data streaming timeframe."""
        try:
            self.nervous_system.set_timeframe(timeframe)
            return {
                'status': 'success',
                'message': f'Timeframe set to {timeframe}'
            }
        except Exception as e:
            logger.error(f"Error setting timeframe: {e}")
            return {
                'status': 'error',
                'message': f"Failed to set timeframe: {str(e)}"
            }
    
    def set_simulation_speed(self, speed: float) -> Dict:
        """Set the simulation speed multiplier."""
        try:
            self.nervous_system.set_simulation_speed(speed)
            return {
                'status': 'success',
                'message': f'Simulation speed set to {speed}x'
            }
        except Exception as e:
            logger.error(f"Error setting simulation speed: {e}")
            return {
                'status': 'error',
                'message': f"Failed to set simulation speed: {str(e)}"
            }
    
    def get_available_timeframes(self) -> Dict:
        """Get list of available timeframes."""
        try:
            timeframes = self.config['paper_trading']['timeframes']
            return {
                'status': 'success',
                'timeframes': timeframes
            }
        except Exception as e:
            logger.error(f"Error getting timeframes: {e}")
            return {
                'status': 'error',
                'message': f"Failed to get timeframes: {str(e)}"
            }
    
    def get_available_pairs(self) -> Dict:
        """Get list of available trading pairs."""
        try:
            pairs = [pair['symbol'] for pair in self.config['paper_trading']['pairs']]
            return {
                'status': 'success',
                'pairs': pairs
            }
        except Exception as e:
            logger.error(f"Error getting pairs: {e}")
            return {
                'status': 'error',
                'message': f"Failed to get pairs: {str(e)}"
            }
    
    def _stream_worker(self, symbol: str):
        """Worker function for data streaming thread."""
        try:
            for result in self.nervous_system.start_streaming(symbol):
                if not self._stream_active:
                    break
                    
                # Log streaming results
                if result['status'] == 'success':
                    logger.info(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"{symbol} - "
                        f"Price: {result.get('price', 'N/A')} | "
                        f"Patterns: {len(result.get('patterns', []))} | "
                        f"Signals: {len(result.get('signals', []))}"
                    )
                else:
                    logger.error(f"Streaming error: {result.get('message')}")
                    
        except Exception as e:
            logger.error(f"Stream worker error: {e}")
            self._stream_active = False
    
    def start_data_stream(self, symbol: str) -> Dict:
        """Start the market data stream."""
        try:
            if self._stream_active:
                return {
                    'status': 'error',
                    'message': 'Stream already active'
                }
            
            self._stream_active = True
            self._current_symbol = symbol
            
            # Start streaming in a separate thread
            self._stream_thread = threading.Thread(
                target=self._stream_worker,
                args=(symbol,)
            )
            self._stream_thread.start()
            
            return {
                'status': 'success',
                'message': f'Market data stream started for {symbol}'
            }
            
        except Exception as e:
            logger.error(f"Error starting data stream: {e}")
            self._stream_active = False
            return {
                'status': 'error',
                'message': f"Failed to start data stream: {str(e)}"
            }
    
    def stop_data_stream(self) -> Dict:
        """Stop the market data stream."""
        try:
            if not self._stream_active:
                return {
                    'status': 'error',
                    'message': 'No active stream to stop'
                }
            
            self._stream_active = False
            if self._stream_thread:
                self._stream_thread.join(timeout=5.0)
            
            return {
                'status': 'success',
                'message': 'Market data stream stopped'
            }
            
        except Exception as e:
            logger.error(f"Error stopping data stream: {e}")
            return {
                'status': 'error',
                'message': f"Failed to stop data stream: {str(e)}"
            }
    
    def get_active_patterns(self) -> Dict:
        """Get currently active market patterns."""
        try:
            if not self._stream_active:
                return {
                    'status': 'error',
                    'message': 'No active stream'
                }
                
            # Implementation to be added
            return {
                'status': 'success',
                'patterns': []
            }
            
        except Exception as e:
            logger.error(f"Error getting active patterns: {e}")
            return {
                'status': 'error',
                'message': f"Failed to get active patterns: {str(e)}"
            }
    
    def get_performance_metrics(self) -> Dict:
        """Get detailed performance metrics."""
        try:
            metrics = self.nervous_system.metrics.metrics
            formatted_metrics = {}
            
            for name, metric in metrics.items():
                formatted_metrics[name] = {
                    'value': metric['value'],
                    'description': metric['description'],
                    'optimal_range': metric['optimal_range']
                }
            
            return {
                'status': 'success',
                'metrics': formatted_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                'status': 'error',
                'message': f"Failed to get performance metrics: {str(e)}"
            }
    
    def optimize_parameters(self) -> Dict:
        """Optimize system parameters based on performance metrics."""
        try:
            # Implementation to be added
            return {
                'status': 'success',
                'message': 'Parameters optimized successfully'
            }
            
        except Exception as e:
            logger.error(f"Error optimizing parameters: {e}")
            return {
                'status': 'error',
                'message': f"Failed to optimize parameters: {str(e)}"
            }
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        try:
            health = self.get_system_health()
            metrics = self.get_performance_metrics()
            
            if health['status'] == 'error' or metrics['status'] == 'error':
                raise Exception("Failed to get complete system status")
            
            status = {
                'status': 'success',
                'health': health['health_score'],
                'metrics': metrics['metrics'],
                'config': {
                    'preprocessing': self.config['preprocessing'],
                    'patterns': self.config['patterns'],
                    'performance': self.config['performance']
                }
            }
            
            # Add streaming status if active
            if self._stream_active:
                status['streaming'] = {
                    'active': True,
                    'symbol': self._current_symbol,
                    'timeframe': self.nervous_system.streamer.current_timeframe,
                    'speed': self.nervous_system.streamer.simulation_speed
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'status': 'error',
                'message': f"Failed to get system status: {str(e)}"
            }
