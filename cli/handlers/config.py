"""
Handler per la Gestione della Configurazione
"""
import time
import yaml
from pathlib import Path
from rich.table import Table
from typing import Dict, Any, Optional

from cli.utils import show_progress, console, print_error, print_success
from utils.logger_base import get_component_logger
from utils.config import load_config, validate_config

# Setup logger
logger = get_component_logger('CLI.Config')

def get_optimization_range(config: Dict[str, Any], param_path: str) -> Optional[str]:
    """Recupera il range di ottimizzazione per un parametro se disponibile"""
    try:
        if "optimization" in config and isinstance(config["optimization"], dict):
            # Gestione percorsi nidificati (es: "rsi.period")
            parts = param_path.split(".")
            current = config["optimization"]
            for part in parts:
                if part in current:
                    current = current[part]
                    if isinstance(current, list) and len(current) == 2:
                        return f"{current[0]} - {current[1]}"
        return None
    except (KeyError, TypeError, IndexError):
        return None

def create_config_table(title: str, data: Dict[str, Any], config: Dict[str, Any], parent_key: str = "") -> Table:
    """Crea una tabella Rich per una sezione della configurazione"""
    table = Table(title=f"[bold cyan]{title}[/]", show_header=True, header_style="bold magenta")
    table.add_column("Parametro", style="cyan")
    table.add_column("Valore", style="green")
    table.add_column("Range Ottimizzazione", style="yellow")
    table.add_column("Note", style="blue")

    def add_to_table(d: Dict[str, Any], prefix: str = ""):
        for key, value in d.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                add_to_table(value, f"{full_key}.")
            else:
                # Gestione speciale per liste e booleani
                if isinstance(value, list):
                    value_str = ", ".join(map(str, value))
                elif isinstance(value, bool):
                    value_str = "✓" if value else "✗"
                else:
                    value_str = str(value)
                
                # Recupera range di ottimizzazione
                opt_range = get_optimization_range(config, full_key)
                
                # Aggiungi note per valori speciali
                note = ""
                if isinstance(value, (int, float)):
                    if "timeout" in key.lower():
                        note = "millisecondi"
                    elif "size" in key.lower():
                        note = "bytes"
                    elif "rate" in key.lower():
                        note = "ratio"
                    elif "period" in key.lower():
                        note = "periodi"
                    elif "threshold" in key.lower():
                        note = "soglia"
                
                table.add_row(full_key, value_str, opt_range or "", note)
    
    add_to_table(data)
    return table

def display_config_section(config: Dict[str, Any], section_name: str) -> None:
    """Visualizza una sezione della configurazione in formato tabellare"""
    if isinstance(config, dict):
        # Gestione speciale per sezioni con indicatori
        if section_name.lower() == "dna" and "indicators" in config:
            # Tabella principale DNA
            main_table = create_config_table(f"{section_name} - General", 
                                          {k: v for k, v in config.items() if k != "indicators"},
                                          config)
            console.print(main_table)
            console.print()
            
            # Tabelle per ogni indicatore
            if isinstance(config["indicators"], dict):
                for ind_name, ind_config in config["indicators"].items():
                    if isinstance(ind_config, dict):
                        ind_table = create_config_table(f"Indicator - {ind_name}", 
                                                      ind_config,
                                                      config)
                        console.print(ind_table)
                        console.print()
        else:
            # Crea tabelle per sottosezioni principali
            for key, value in config.items():
                if isinstance(value, dict):
                    subsection_table = create_config_table(f"{section_name} - {key}", 
                                                         {key: value},
                                                         config)
                    console.print(subsection_table)
                    console.print()
                else:
                    # Per valori singoli, crea una tabella semplice
                    simple_table = Table(show_header=True, header_style="bold magenta")
                    simple_table.add_column("Parametro", style="cyan")
                    simple_table.add_column("Valore", style="green")
                    simple_table.add_column("Range Ottimizzazione", style="yellow")
                    simple_table.add_row(key, str(value), "")
                    console.print(simple_table)
                    console.print()

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
            
            # Visualizza ogni file di configurazione in formato tabellare
            for config_name, config_data in config.items():
                console.print(f"\n[bold cyan]{config_name.upper()}[/]")
                display_config_section(config_data, config_name)
                
            logger.info("Visualizzazione configurazione completata")
            
        except Exception as e:
            logger.error(f"Errore durante la visualizzazione: {str(e)}")
            print_error(f"Errore durante la visualizzazione: {str(e)}")
    
    else:
        logger.warning(f"Azione non valida: {args.action}")
        print_error(f"Azione non valida: {args.action}")