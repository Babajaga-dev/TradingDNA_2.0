"""
Handler per il Sistema di Logging
"""
import time
import yaml
from pathlib import Path
from rich.table import Table

from cli.utils import show_progress, console, create_progress, print_error
from core.base_exchange import BaseExchange
from core.dna_downloader import DNADataDownloader
from utils.logger_base import get_component_logger

# Setup logger
logger = get_component_logger('CLI.Log')

def print_log_menu() -> Table:
    """Crea e restituisce la tabella del menu log"""
    table = Table(show_header=False, border_style="cyan", box=None)
    table.add_column("Option", style="cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("[1]", "📊 Visualizza Dati    - Mostra dati scaricati")
    table.add_row("[2]", "📝 Visualizza Log     - Mostra log sistema")
    table.add_row("[3]", "🗑️  Pulisci Log       - Cancella log")
    table.add_row("", "")
    table.add_row("[0]", "🔙 Indietro")
    
    return table

def handle_data_view():
    """Gestisce la visualizzazione dei dati"""
    try:
        # Carica configurazione
        with open('config/dna.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Ottieni lista simboli e timeframes disponibili
        symbols = set()
        timeframes = set()
        for dataset_type in ['training', 'testing', 'paper_trading']:
            if dataset_type in config['data']:
                for pair in config['data'][dataset_type]['pairs']:
                    symbols.add(pair['symbol'])
                    timeframes.update(pair['timeframes'])
        
        # Converti in liste ordinate
        symbols = sorted(list(symbols))
        timeframes = sorted(list(timeframes))
        
        # Menu selezione simbolo
        symbol_table = Table(title="Seleziona Simbolo", show_header=False)
        symbol_table.add_column("Option", style="cyan", width=4)
        symbol_table.add_column("Symbol", style="white")
        
        for i, symbol in enumerate(symbols, 1):
            symbol_table.add_row(f"[{i}]", symbol)
        
        console.print("\n")
        console.print(symbol_table)
        symbol_choice = console.input("\nSeleziona simbolo [cyan][1-{}][/]: ".format(len(symbols)))
        
        if not symbol_choice.isdigit() or int(symbol_choice) < 1 or int(symbol_choice) > len(symbols):
            logger.warning(f"Selezione simbolo non valida: {symbol_choice}")
            print_error("Scelta non valida")
            return
        
        selected_symbol = symbols[int(symbol_choice) - 1]
        
        # Menu selezione timeframe
        tf_table = Table(title="Seleziona Timeframe", show_header=False)
        tf_table.add_column("Option", style="cyan", width=4)
        tf_table.add_column("Timeframe", style="white")
        
        for i, tf in enumerate(timeframes, 1):
            tf_table.add_row(f"[{i}]", tf)
        
        console.print("\n")
        console.print(tf_table)
        tf_choice = console.input("\nSeleziona timeframe [cyan][1-{}][/]: ".format(len(timeframes)))
        
        if not tf_choice.isdigit() or int(tf_choice) < 1 or int(tf_choice) > len(timeframes):
            logger.warning(f"Selezione timeframe non valida: {tf_choice}")
            print_error("Scelta non valida")
            return
        
        selected_tf = timeframes[int(tf_choice) - 1]
        
        # Menu selezione dataset
        dataset_table = Table(title="Seleziona Dataset", show_header=False)
        dataset_table.add_column("Option", style="cyan", width=4)
        dataset_table.add_column("Dataset", style="white")
        
        datasets = ["training", "validation", "testing"]
        for i, ds in enumerate(datasets, 1):
            dataset_table.add_row(f"[{i}]", ds)
        dataset_table.add_row("[4]", "Tutti")
        
        console.print("\n")
        console.print(dataset_table)
        ds_choice = console.input("\nSeleziona dataset [cyan][1-4][/]: ")
        
        if not ds_choice.isdigit() or int(ds_choice) < 1 or int(ds_choice) > 4:
            logger.warning(f"Selezione dataset non valida: {ds_choice}")
            print_error("Scelta non valida")
            return
        
        selected_ds = None if int(ds_choice) == 4 else datasets[int(ds_choice) - 1]
        
        # Visualizza dati
        exchange = BaseExchange("config/network.yaml")
        downloader = DNADataDownloader(exchange)
        logger.info(f"Visualizzazione dati: {selected_symbol} {selected_tf} {selected_ds or 'tutti'}")
        downloader.display_data(selected_symbol, selected_tf, selected_ds)
        
    except Exception as e:
        logger.error(f"Errore visualizzazione dati: {str(e)}")
        print_error(f"Errore visualizzazione dati: {str(e)}")

def handle_log(args=None):
    """Gestisce il comando log"""
    logger.info("Avvio sistema log")
    
    while True:
        console.print("\n[bold cyan]📊 Log & Monitor[/]")
        console.print(print_log_menu())
        choice = console.input("\nSeleziona un'opzione [cyan][0-3][/]: ")
        
        if choice == '0':
            break
            
        elif choice == '1':  # Visualizza Dati
            handle_data_view()
            
        elif choice == '2':  # Visualizza Log
            with show_progress("Caricamento log") as progress:
                task = progress.add_task("Lettura...", total=100)
                for _ in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.02)
            # TODO: Implementare visualizzazione log
            logger.warning("Visualizzazione log non ancora implementata")
            
        elif choice == '3':  # Pulisci Log
            with show_progress("Pulizia log") as progress:
                task = progress.add_task("Cancellazione...", total=100)
                for _ in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.02)
            # TODO: Implementare pulizia log
            logger.warning("Pulizia log non ancora implementata")
            
        else:
            logger.warning(f"Opzione non valida: {choice}")
            print_error("Opzione non valida!")
            time.sleep(1)
            
        console.input("\nPremi INVIO per continuare...")
