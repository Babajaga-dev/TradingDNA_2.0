"""Base logging configuration"""
import logging
import yaml
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

# Tema Rich
custom_theme = Theme({
    'info': 'cyan',
    'warning': 'yellow',
    'error': 'red bold',
    'critical': 'red bold reverse',
    'success': 'green bold'
})

console = Console(theme=custom_theme)

class ComponentLogger:
    """Logger specifico per componenti del sistema"""
    def __init__(self, component_name: str):
        self.name = component_name
        self.logger = logging.getLogger(component_name)
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
        return f"{icon} {self.name:<12} │ {message}"
        
    def debug(self, message: str):
        self.logger.debug(self._format_message(message))
        
    def info(self, message: str):
        self.logger.info(self._format_message(message))
        
    def warning(self, message: str):
        self.logger.warning(self._format_message(message))
        
    def error(self, message: str):
        self.logger.error(self._format_message(message))
        
    def critical(self, message: str):
        self.logger.critical(self._format_message(message))

def get_progress_logger():
    """Ottiene un progress logger configurato con Rich.
    
    Returns:
        Progress: Un context manager per tracciare il progresso delle operazioni
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn()
    )

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
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.warning(f"Errore caricamento config logging: {e}. Usando config base.")
        return None, None

    metrics = LogMetrics()
    storage_manager = LogStorageManager(config)
    
    # Configurazione globale
    log_level = getattr(logging, config['global']['log_level'])
    log_format = config['global']['format']
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
