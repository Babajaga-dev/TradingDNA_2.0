"""Handler per la configurazione del sistema DNA."""
from typing import Dict
import logging
from pathlib import Path
import yaml
from rich.table import Table
from rich import print as rprint

from cli.utils import console, print_error, print_success
from utils.logger_base import get_component_logger
from utils.config import ConfigManager
from core.dna import DNA

logger = get_component_logger('DNAConfig')

class DNAConfigHandler:
    """Handler class for DNA configuration operations."""
    
    def __init__(self, dna: DNA):
        """Initialize the configuration handler."""
        self.dna = dna
        self.config_manager = ConfigManager()
        
    def handle_config(self) -> None:
        """Handle DNA configuration."""
        try:
            # Load current configuration using ConfigManager
            config = self.config_manager.get_config('dna')
            
            # Create configuration table
            config_table = Table(title="Configurazione DNA", border_style="cyan")
            config_table.add_column("Parametro", style="cyan")
            config_table.add_column("Valore", style="white")
            config_table.add_column("Descrizione", style="white")
            
            # Add gene configurations
            if 'indicators' in config:
                for gene_name, params in config['indicators'].items():
                    # Skip non-dictionary items and special keys
                    if not isinstance(params, dict) or gene_name in ['base_path', 'auto_discovery', 'cache_enabled', 'cache_size', 'computation']:
                        continue
                        
                    config_table.add_row(
                        f"[cyan]{gene_name.upper()}[/]",
                        "",
                        "Parametri indicatore"
                    )
                    for param_name, value in params.items():
                        config_table.add_row(
                            f"  {param_name}",
                            str(value),
                            self._get_param_description(gene_name, param_name)
                        )
                    config_table.add_row("", "", "")
            
            console.print("\n")
            console.print(config_table)
            console.print("\n")
            
            # Ask if user wants to modify configuration
            choice = console.input("\nModificare la configurazione? [cyan][s/N][/]: ").lower()
            
            if choice == 's':
                self._modify_config(config)
            
            logger.info("Configurazione completata")
            
        except Exception as e:
            logger.error(f"Errore durante configurazione: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
            
    def _modify_config(self, config: Dict) -> None:
        """Modify DNA configuration."""
        modified = False
        
        if 'indicators' in config:
            for gene_name, params in config['indicators'].items():
                # Skip non-dictionary items and special keys
                if not isinstance(params, dict) or gene_name in ['base_path', 'auto_discovery', 'cache_enabled', 'cache_size', 'computation']:
                    continue
                    
                console.print(f"\n[cyan]Modifica parametri {gene_name.upper()}[/]")
                
                for param_name, value in params.items():
                    new_value = console.input(
                        f"{param_name} [{value}]: "
                    ).strip()
                    
                    if new_value:
                        try:
                            # Convert to appropriate type
                            if isinstance(value, int):
                                params[param_name] = int(new_value)
                            elif isinstance(value, float):
                                params[param_name] = float(new_value)
                            else:
                                params[param_name] = new_value
                            modified = True
                        except ValueError:
                            print_error(f"Valore non valido per {param_name}")
                            continue
        
        if modified:
            # Save configuration
            config_path = Path("config/dna.yaml")
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            print_success("Configurazione salvata con successo")
            
            # Reinitialize DNA with new configuration
            from cli.handlers.dna_base import DNAHandler
            handler = DNAHandler()
            handler.handle_init()
            
    def _get_param_description(self, gene_name: str, param_name: str) -> str:
        """Get parameter description."""
        descriptions = {
            'rsi': {
                'period': 'Periodo per il calcolo RSI',
                'overbought': 'Livello di ipercomprato',
                'oversold': 'Livello di ipervenduto',
                'signal_threshold': 'Soglia del segnale',
                'weight': 'Peso del segnale'
            },
            'macd': {
                'fast_period': 'Periodo media mobile veloce',
                'slow_period': 'Periodo media mobile lenta',
                'signal_period': 'Periodo linea del segnale',
                'signal_threshold': 'Soglia del segnale',
                'weight': 'Peso del segnale'
            },
            'bollinger': {
                'period': 'Periodo per le bande',
                'num_std': 'Deviazioni standard',
                'signal_threshold': 'Soglia del segnale',
                'weight': 'Peso del segnale'
            },
            'volume': {
                'vwap_period': 'Periodo VWAP',
                'volume_ma_period': 'Periodo media mobile volume',
                'signal_threshold': 'Soglia del segnale',
                'weight': 'Peso del segnale'
            },
            'pattern_recognition': {
                'min_pattern_length': 'Lunghezza minima pattern',
                'max_pattern_length': 'Lunghezza massima pattern',
                'min_confidence': 'Confidenza minima',
                'similarity_threshold': 'Soglia similarità',
                'correlation_weight': 'Peso correlazione',
                'length_weight': 'Peso lunghezza',
                'quality_threshold': 'Soglia qualità'
            },
            'strong_signal': {
                'window_size': 'Dimensione finestra',
                'trend_threshold': 'Soglia trend',
                'signal_multiplier': 'Moltiplicatore segnale',
                'weight': 'Peso del segnale'
            }
        }
        
        return descriptions.get(gene_name, {}).get(param_name, "")
