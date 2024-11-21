"""
Comandi CLI per TradingDNA 2.0
"""
import time
import sys
from rich.table import Table

from cli.utils import show_progress, console, print_error
from cli.handlers import (
    handle_dna, 
    handle_log, 
    handle_download, 
    handle_config
)
from utils.logger import get_component_logger
from utils.initializer import Initializer, InitializationError

# Setup logger
logger = get_component_logger('CLI')

def handle_immune():
    """Gestisce il Sistema Immunitario"""
    with show_progress("Sistema Immunitario") as progress:
        task = progress.add_task("Analisi rischi...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[red]Sistema Immunitario - Non ancora implementato[/]")

def handle_metabolism():
    """Gestisce il Sistema Metabolismo"""
    with show_progress("Sistema Metabolismo") as progress:
        task = progress.add_task("Analisi capitale...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[green]Sistema Metabolismo - Non ancora implementato[/]")

def handle_nervous():
    """Gestisce il Sistema Nervoso"""
    with show_progress("Sistema Nervoso") as progress:
        task = progress.add_task("Analisi dati...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[blue]Sistema Nervoso - Non ancora implementato[/]")

def handle_endocrine():
    """Gestisce il Sistema Endocrino"""
    with show_progress("Sistema Endocrino") as progress:
        task = progress.add_task("Ottimizzazione parametri...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[magenta]Sistema Endocrino - Non ancora implementato[/]")

def handle_reproductive():
    """Gestisce il Sistema Riproduttivo"""
    with show_progress("Sistema Riproduttivo") as progress:
        task = progress.add_task("Evoluzione strategie...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[yellow]Sistema Riproduttivo - Non ancora implementato[/]")

def handle_init(args):
    """Gestisce il comando init"""
    logger.info("Avvio inizializzazione sistema")
    try:
        initializer = Initializer(force=args.force)
        initializer.initialize()  # Chiamata una sola volta
        
        # Progress bar solo se l'inizializzazione ha successo
        with show_progress("Inizializzazione sistema") as progress:
            task = progress.add_task("Setup completato", total=100)
            progress.update(task, advance=100)  # Aggiorna subito al 100%
            
    except InitializationError as e:
        logger.error(f"Errore di inizializzazione: {str(e)}")
        print_error(f"Errore di inizializzazione: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Errore: {str(e)}")
        print_error(f"Errore: {str(e)}")
        sys.exit(1)
        
    logger.info("Inizializzazione completata con successo")
    return True
