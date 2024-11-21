"""
Modulo di logging per TradingDNA 2.0 con supporto visual
"""
import logging
import logging.handlers
import yaml
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

# Configurazione tema Rich
custom_theme = Theme({
    'info': 'cyan',
    'warning': 'yellow',
    'error': 'red bold',
    'critical': 'red bold reverse',
    'success': 'green bold'
})

console = Console(theme=custom_theme)

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

class ProgressLogger:
    """Logger per progress bars"""
    def __init__(self, console=console):
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

def setup_logging(config_file: str = None) -> None:
    """
    Configura il sistema di logging basato sul file di configurazione
    
    Args:
        config_file: Percorso al file di configurazione trace.yaml
    """
    if config_file is None:
        config_file = Path(__file__).parent.parent / "config" / "trace.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        # Fallback su configurazione base in caso di errore
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.warning(f"Errore caricamento config logging: {e}. Usando config base.")
        return

    # Configurazione globale
    log_level = getattr(logging, config['global']['log_level'])
    log_format = config['global']['format']
    date_format = config['global']['date_format']
    
    # Configurazione root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format
    )
    
    # Disabilita propagazione per moduli specifici
    for module in config.get('modules', {}):
        logger = logging.getLogger(module)
        logger.propagate = False
        
        # Livello log specifico per modulo
        module_level = getattr(logging, config['modules'][module]['level'])
        logger.setLevel(module_level)
        
        # File handler per modulo
        if config['file']['enabled']:
            log_dir = Path(config['file']['path'])
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_dir / config['modules'][module]['file'],
                maxBytes=config['file']['max_size_mb'] * 1024 * 1024,
                backupCount=config['file']['backup_count'],
                encoding=config['global']['encoding']
            )
            file_handler.setFormatter(logging.Formatter(log_format, date_format))
            logger.addHandler(file_handler)
        
        # Console handler per modulo
        if config['console']['enabled'] and config['modules'][module].get('console', True):
            if config['console'].get('visual', True):
                # Usa il visual handler se abilitato
                console_handler = VisualLogHandler()
            else:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter(log_format, date_format))
            logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Ottiene un logger configurato per il modulo specificato
    
    Args:
        name: Nome del modulo
        
    Returns:
        Logger configurato per il modulo
    """
    return logging.getLogger(name)

def get_component_logger(name: str) -> ComponentLogger:
    """
    Ottiene un ComponentLogger per il componente specificato
    
    Args:
        name: Nome del componente (dna, immune, etc.)
        
    Returns:
        ComponentLogger configurato per il componente
    """
    return ComponentLogger(name)

def get_progress_logger() -> ProgressLogger:
    """
    Ottiene un ProgressLogger per visualizzare progress bars
    
    Returns:
        ProgressLogger configurato
    """
    return ProgressLogger()
