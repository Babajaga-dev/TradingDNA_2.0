"""Base logging configuration"""
import logging
import yaml
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from queue import Queue
from threading import Lock

# Tema Rich
custom_theme = Theme({
    'info': 'cyan',
    'warning': 'yellow',
    'error': 'red bold',
    'critical': 'red bold reverse',
    'success': 'green bold'
})

console = Console(theme=custom_theme)
_progress_active = False
_message_queue = Queue()
_lock = Lock()
_initialization_shown = False

class ComponentLogger:
    """Logger specifico per componenti del sistema"""
    def __init__(self, component_name: str):
        # Gestisce i nomi composti prendendo solo l'ultima parte
        self.name = component_name.split('.')[-1]
        self.logger = logging.getLogger('system')  # Usa un logger generico
        self.icons = {
            'DNA': '🧬',
            'IMMUNE': '🛡️',
            'METABOLISM': '⚡',
            'NERVOUS': '🧠',
            'ENDOCRINE': '⚖️',
            'REPRODUCTIVE': '🔄'
        }
        
    def _format_message(self, message: str) -> str:
        """Formatta il messaggio con icona del componente"""
        icon = self.icons.get(self.name.upper(), '•')
        # Usa esattamente 15 caratteri per il nome del componente
        component_name = f"{self.name:<15}"
        return f"{icon} {component_name}│ {message}"
        
    def _log_message(self, level: int, message: str):
        global _progress_active, _initialization_shown
        formatted_message = self._format_message(message)
        
        with _lock:
            if message == "Inizializzazione DNA system" and not _initialization_shown:
                _initialization_shown = True
                console.print("\nInizializzazione DNA system...\n")
            elif _progress_active or "Aggiunto gene" in message or "Stato DNA salvato" in message:
                _message_queue.put((level, formatted_message))
            else:
                self.logger.log(level, formatted_message)
        
    def debug(self, message: str):
        self._log_message(logging.DEBUG, message)
        
    def info(self, message: str):
        self._log_message(logging.INFO, message)
        
    def warning(self, message: str):
        self._log_message(logging.WARNING, message)
        
    def error(self, message: str):
        self._log_message(logging.ERROR, message)
        
    def critical(self, message: str):
        self._log_message(logging.CRITICAL, message)

class ProgressLoggerWrapper:
    """Wrapper per il Progress logger che gestisce l'accodamento dei messaggi"""
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description:<50}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            transient=True,  # Rimuove la barra quando completata
            expand=True
        )
        
    def __enter__(self):
        global _progress_active
        _progress_active = True
        return self.progress.__enter__()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _progress_active
        result = self.progress.__exit__(exc_type, exc_val, exc_tb)
        _progress_active = False
        
        console.print()  # Aggiunge una riga vuota dopo la barra
        
        # Processa i messaggi in coda
        while not _message_queue.empty():
            level, message = _message_queue.get()
            logging.getLogger('system').log(level, message)
        
        return result

def get_progress_logger():
    """Ottiene un progress logger configurato con Rich."""
    return ProgressLoggerWrapper()

def setup_logging(config_file: str = None):
    """Configura il sistema di logging"""
    from .logger_metrics import LogMetrics
    from .logger_storage import LogStorageManager
    from .logger_handlers import MetricsHandler, VisualLogHandler, SizeRotatingFileHandler
    
    if config_file is None:
        config_file = Path(__file__).parent.parent / "config" / "trace.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s'  # Formato minimo
        )
        logging.warning(f"Errore caricamento config logging: {e}. Usando config base.")
        return None, None

    metrics = LogMetrics()
    storage_manager = LogStorageManager(config)
    
    # Configurazione globale
    log_level = getattr(logging, config['global']['log_level'])
    log_format = '%(asctime)s - %(message)s'  # Formato minimo
    date_format = config['global']['date_format']
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format
    )
    
    # Handler metriche
    root_logger = logging.getLogger()
    metrics_handler = MetricsHandler(metrics)
    root_logger.addHandler(metrics_handler)
    
    # Configura moduli
    for module in config.get('modules', {}):
        logger = logging.getLogger(module)
        logger.propagate = False
        
        module_level = getattr(logging, config['modules'][module]['level'])
        logger.setLevel(module_level)
        
        if config['file']['enabled']:
            log_dir = Path(config['file']['path'])
            log_dir.mkdir(exist_ok=True)
            
            file_handler = SizeRotatingFileHandler(
                log_dir / config['modules'][module]['file'],
                storage_manager,
                backupCount=config['file']['backup_count'],
                encoding=config['global']['encoding']
            )
            file_handler.setFormatter(logging.Formatter(log_format, date_format))
            logger.addHandler(file_handler)
        
        if config['console']['enabled'] and config['modules'][module].get('console', True):
            if config['console'].get('visual', True):
                console_handler = VisualLogHandler()
            else:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter(log_format, date_format))
            logger.addHandler(console_handler)
            
    return metrics, storage_manager

def get_logger(name: str) -> logging.Logger:
    """Ottiene un logger configurato"""
    return logging.getLogger(name)

def get_component_logger(name: str) -> ComponentLogger:
    """Ottiene un ComponentLogger"""
    return ComponentLogger(name)
