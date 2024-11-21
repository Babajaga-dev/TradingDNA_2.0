"""
Modulo di logging per TradingDNA 2.0
"""
import logging
import logging.handlers
import yaml
from pathlib import Path

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
