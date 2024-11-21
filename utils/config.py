"""
Modulo di gestione configurazione per TradingDNA 2.0
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigError(Exception):
    """Eccezione per errori di configurazione"""
    pass

def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Carica la configurazione da un file YAML
    
    Args:
        config_file: Percorso al file di configurazione. Se None, carica tutti i file .yaml dalla directory config/
        
    Returns:
        Dizionario con la configurazione caricata
        
    Raises:
        ConfigError: Se ci sono errori nel caricamento della configurazione
    """
    config_dir = Path(__file__).parent.parent / "config"
    
    if config_file:
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = config_dir / config_path
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ConfigError(f"Errore caricamento {config_path}: {str(e)}")
    
    # Carica tutti i file .yaml dalla directory config/
    config = {}
    for yaml_file in config_dir.glob("*.yaml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config[yaml_file.stem] = yaml.safe_load(f)
        except Exception as e:
            raise ConfigError(f"Errore caricamento {yaml_file}: {str(e)}")
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Valida la configurazione
    
    Args:
        config: Dizionario con la configurazione da validare
        
    Returns:
        True se la configurazione è valida, False altrimenti
        
    Raises:
        ConfigError: Se ci sono errori nella validazione
    """
    # TODO: Implementare validazione configurazione
    return True

def get_config_path(filename: str) -> Path:
    """
    Ottiene il percorso completo di un file di configurazione
    
    Args:
        filename: Nome del file di configurazione
        
    Returns:
        Path completo al file di configurazione
    """
    return Path(__file__).parent.parent / "config" / filename
