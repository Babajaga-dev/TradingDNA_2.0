"""
Metriche di performance del sistema
"""
from dataclasses import dataclass
from typing import Dict, List
import time
import psutil
import numpy as np
from collections import deque

from utils.logger_base import get_component_logger

# Setup logger
logger = get_component_logger('Metrics.Performance')

@dataclass
class PerformanceMetrics:
    """Metriche di performance del sistema."""
    
    def __init__(self, window_size: int = 100):
        """
        Inizializza le metriche di performance.
        
        Args:
            window_size: Dimensione della finestra per le medie mobili
        """
        # Metriche di sistema
        self.cpu_usage: float = 0.0
        self.memory_usage: float = 0.0
        self.disk_io: float = 0.0
        
        # Metriche di latenza
        self.signal_latency: float = 0.0
        self.execution_latency: float = 0.0
        self.total_latency: float = 0.0
        
        # Metriche di throughput
        self.signals_per_second: float = 0.0
        self.trades_per_second: float = 0.0
        
        # Code per medie mobili
        self._window_size = window_size
        self._signal_latencies = deque(maxlen=window_size)
        self._execution_latencies = deque(maxlen=window_size)
        self._cpu_readings = deque(maxlen=window_size)
        self._memory_readings = deque(maxlen=window_size)
        
        # Timestamp per calcolo throughput
        self._last_signal_time = time.time()
        self._last_trade_time = time.time()
        self._signal_count = 0
        self._trade_count = 0
        
        logger.info(f"Inizializzate metriche performance con window_size={window_size}")
        
    def update_system_metrics(self) -> None:
        """Aggiorna le metriche di sistema."""
        try:
            # CPU usage
            cpu = psutil.cpu_percent()
            self._cpu_readings.append(cpu)
            self.cpu_usage = np.mean(self._cpu_readings)
            
            # Memory usage
            memory = psutil.Process().memory_percent()
            self._memory_readings.append(memory)
            self.memory_usage = np.mean(self._memory_readings)
            
            # Disk I/O
            disk = psutil.disk_io_counters()
            self.disk_io = disk.read_bytes + disk.write_bytes if disk else 0
            
            logger.debug(f"Metriche sistema aggiornate: CPU={self.cpu_usage:.1f}%, "
                        f"MEM={self.memory_usage:.1f}%")
                        
        except Exception as e:
            logger.error(f"Errore aggiornamento metriche sistema: {str(e)}")
            
    def record_signal_latency(self, latency: float) -> None:
        """
        Registra la latenza di un segnale.
        
        Args:
            latency: Latenza in millisecondi
        """
        self._signal_latencies.append(latency)
        self.signal_latency = np.mean(self._signal_latencies)
        
        # Aggiorna throughput segnali
        current_time = time.time()
        self._signal_count += 1
        elapsed = current_time - self._last_signal_time
        
        if elapsed >= 1.0:  # Aggiorna ogni secondo
            self.signals_per_second = self._signal_count / elapsed
            self._signal_count = 0
            self._last_signal_time = current_time
            
        logger.debug(f"Registrata latenza segnale: {latency:.2f}ms, "
                    f"media={self.signal_latency:.2f}ms")
            
    def record_execution_latency(self, latency: float) -> None:
        """
        Registra la latenza di esecuzione.
        
        Args:
            latency: Latenza in millisecondi
        """
        self._execution_latencies.append(latency)
        self.execution_latency = np.mean(self._execution_latencies)
        self.total_latency = self.signal_latency + self.execution_latency
        
        # Aggiorna throughput trade
        current_time = time.time()
        self._trade_count += 1
        elapsed = current_time - self._last_trade_time
        
        if elapsed >= 1.0:  # Aggiorna ogni secondo
            self.trades_per_second = self._trade_count / elapsed
            self._trade_count = 0
            self._last_trade_time = current_time
            
        logger.debug(f"Registrata latenza esecuzione: {latency:.2f}ms, "
                    f"media={self.execution_latency:.2f}ms")
            
    def get_latency_stats(self) -> Dict[str, float]:
        """Calcola statistiche sulle latenze."""
        signal_stats = {
            'min': np.min(self._signal_latencies) if self._signal_latencies else 0,
            'max': np.max(self._signal_latencies) if self._signal_latencies else 0,
            'std': np.std(self._signal_latencies) if self._signal_latencies else 0
        }
        
        exec_stats = {
            'min': np.min(self._execution_latencies) if self._execution_latencies else 0,
            'max': np.max(self._execution_latencies) if self._execution_latencies else 0,
            'std': np.std(self._execution_latencies) if self._execution_latencies else 0
        }
        
        return {
            'signal_latency': signal_stats,
            'execution_latency': exec_stats,
            'total_latency': self.total_latency
        }
        
    def to_dict(self) -> Dict[str, float]:
        """Converte le metriche in dizionario."""
        return {
            # Metriche sistema
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_io': self.disk_io,
            
            # Metriche latenza
            'signal_latency': self.signal_latency,
            'execution_latency': self.execution_latency,
            'total_latency': self.total_latency,
            
            # Metriche throughput
            'signals_per_second': self.signals_per_second,
            'trades_per_second': self.trades_per_second
        }
        
    def get_health_score(self) -> float:
        """Calcola uno score di salute del sistema."""
        # Pesi per le diverse metriche
        weights = {
            'cpu': 0.3,
            'memory': 0.2,
            'latency': 0.5
        }
        
        # Normalizza le metriche
        cpu_score = max(0, 1 - (self.cpu_usage / 100))
        memory_score = max(0, 1 - (self.memory_usage / 100))
        latency_score = max(0, 1 - (self.total_latency / 1000))  # Assume max 1s latency
        
        # Calcola score pesato
        health_score = (
            weights['cpu'] * cpu_score +
            weights['memory'] * memory_score +
            weights['latency'] * latency_score
        )
        
        logger.info(f"Calcolato health score: {health_score:.2f}")
        return health_score
