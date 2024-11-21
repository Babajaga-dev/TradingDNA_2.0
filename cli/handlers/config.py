"""
Handler per la Gestione della Configurazione
"""
import time
import yaml
from pathlib import Path
from rich.table import Table

from cli.utils import show_progress, console, print_error, print_success
from utils.logger import get_component_logger
from utils.config import load_config, validate_config

# Setup logger
logger = get_component_logger('CLI.Config')

def display_config(config: dict, indent: int = 0) -> None:
    """Visualizza la configurazione in modo ricorsivo"""
    for key, value in config.items():
        if isinstance(value, dict):
            console.print("  " * indent + f"[cyan]{key}:[/]")
            display_config(value, indent + 1)
        else:
            console.print("  " * indent + f"[cyan]{key}:[/] {value}")

def handle_config(args):
    """Gestisce il comando config"""
    logger.info(f"Gestione configurazione: {args.action}")
    
    if args.action == "validate":
        with show_progress("Validazione configurazione") as progress:
            task = progress.add_task("Controllo...", total=100)
            
            try:
                # Carica tutte le configurazioni
                config = load_config()
                progress.update(task, advance=50)
                
                # Valida le configurazioni
                if validate_config(config):
                    progress.update(task, advance=50)
                    print_success("Configurazione valida")
                    logger.info("Validazione configurazione completata con successo")
                else:
                    print_error("Configurazione non valida")
                    logger.error("Validazione configurazione fallita")
                    
            except Exception as e:
                logger.error(f"Errore durante la validazione: {str(e)}")
                print_error(f"Errore durante la validazione: {str(e)}")
                
    elif args.action == "show":
        try:
            # Carica tutte le configurazioni
            config = load_config()
            
            # Visualizza ogni file di configurazione
            for config_name, config_data in config.items():
                console.print(f"\n[bold cyan]{config_name.upper()}[/]")
                display_config(config_data)
                
            logger.info("Visualizzazione configurazione completata")
            
        except Exception as e:
            logger.error(f"Errore durante la visualizzazione: {str(e)}")
            print_error(f"Errore durante la visualizzazione: {str(e)}")
    
    else:
        logger.warning(f"Azione non valida: {args.action}")
        print_error(f"Azione non valida: {args.action}")
