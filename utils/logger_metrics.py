"""Sistema di metriche per il logging"""
import time
import psutil
from typing import List, Dict

class LogMetrics:
    """Gestore delle metriche di logging"""
    def __init__(self):
        self.log_counts = {
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0
        }
        self.last_error_time = None
        self.error_intervals: List[float] = []
        self.last_reset = time.time()
        
    def increment_count(self, level: str):
        """Incrementa il contatore per un livello di log"""
        self.log_counts[level] = self.log_counts.get(level, 0) + 1
        
        if level in ['ERROR', 'CRITICAL']:
            current_time = time.time()
            if self.last_error_time is not None:
                self.error_intervals.append(current_time - self.last_error_time)
            self.last_error_time = current_time
            
    def get_mttf(self) -> float:
        """Calcola il Mean Time To Failure"""
        if not self.error_intervals:
            return float('inf')
        return sum(self.error_intervals) / len(self.error_intervals)
        
    def reset_counts(self):
        """Resetta i contatori"""
        self.log_counts = {k: 0 for k in self.log_counts}
        self.last_reset = time.time()
        
    def get_metrics(self) -> Dict:
        """Ottiene tutte le metriche correnti"""
        return {
            'counts': self.log_counts.copy(),
            'mttf': self.get_mttf(),
            'uptime': time.time() - self.last_reset
        }

class PerformanceMonitor:
    """Monitor delle performance di logging"""
    def __init__(self):
        self.start_time = time.time()
        self.write_times: List[float] = []
        
    def record_write(self, duration: float):
        """Registra il tempo di scrittura di un log"""
        self.write_times.append(duration)
        if len(self.write_times) > 1000:  # Mantieni solo ultimi 1000 campioni
            self.write_times = self.write_times[-1000:]
            
    def get_metrics(self) -> Dict:
        """Ottiene metriche di performance"""
        if not self.write_times:
            avg_write_time = 0
        else:
            avg_write_time = sum(self.write_times) / len(self.write_times)
            
        return {
            'avg_write_time': avg_write_time,
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
            'uptime': time.time() - self.start_time
        }
