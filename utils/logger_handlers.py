"""Handler personalizzati per il sistema di logging"""
import logging
import logging.handlers
import time
from rich.logging import RichHandler
from .logger_metrics import LogMetrics, PerformanceMonitor
from .logger_storage import LogStorageManager
from .logger_base import console

class MetricsHandler(logging.Handler):
    """Handler per raccolta metriche"""
    def __init__(self, metrics: LogMetrics):
        super().__init__()
        self.metrics = metrics
        
    def emit(self, record):
        self.metrics.increment_count(record.levelname)

class VisualLogHandler(RichHandler):
    """Handler personalizzato per log visuali con Rich"""
    def __init__(self):
        super().__init__(
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            show_time=True,
            show_path=False,
            console=console
        )
        
    def emit(self, record):
        # Aggiunge emoji based on level
        level_icons = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨',
            'SUCCESS': '✅'
        }
        record.icon = level_icons.get(record.levelname, '•')
        super().emit(record)

class SizeRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Handler con controllo dimensione file"""
    def __init__(self, filename, storage_manager: LogStorageManager, **kwargs):
        max_bytes = storage_manager.max_file_size
        super().__init__(filename, maxBytes=max_bytes, **kwargs)
        self.storage_manager = storage_manager
        self.performance_monitor = PerformanceMonitor()
        
    def emit(self, record):
        start_time = time.time()
        
        try:
            if not self.storage_manager.check_total_size():
                self.storage_manager.clean_old_logs()
                
            if self.shouldRollover(record):
                self.doRollover()
                
            super().emit(record)
            
            duration = time.time() - start_time
            self.performance_monitor.record_write(duration)
            
        except Exception as e:
            self.handleError(record)

class ProgressLogger:
    """Logger per progress bars"""
    def __init__(self, console=console):
        from rich.progress import Progress, SpinnerColumn, BarColumn
        from rich.progress import TextColumn, TimeElapsedColumn
        
        self.console = console
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        )
        
    def __enter__(self):
        self.progress.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()
        
    def add_task(self, description: str, total: float) -> int:
        """Aggiunge un nuovo task alla progress bar"""
        return self.progress.add_task(description, total=total)
        
    def update(self, task_id: int, advance: float = 1):
        """Aggiorna il progresso di un task"""
        self.progress.update(task_id, advance=advance)
