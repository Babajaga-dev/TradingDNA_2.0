#!/usr/bin/env python3
"""
TradingDNA 2.0 - Command Line Interface
"""
import sys
import time
import argparse
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
import yaml
from datetime import datetime, timedelta

from utils.logger import setup_logging
from utils.config import load_config
from utils.initializer import Initializer, InitializationError

# Console per output formattato
console = Console()

def print_ascii_logo():
    """Stampa il logo ASCII di TradingDNA 2.0"""
    logo = Panel(Text("""
████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗     
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝     
   ██║   ██████╔╝███████║██║  ██║██║██╔██╗ ██║██║  ███╗    
   ██║   ██╔══██╗██╔══██║██║  ██║██║██║╚██╗██║██║   ██║    
   ██║   ██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝    
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝     
                                                            
                  ██████╗ ███╗   ██╗ █████╗                
                  ██╔══██╗████╗  ██║██╔══██╗               
                  ██║  ██║██╔██╗ ██║███████║               
                  ██║  ██║██║╚██╗██║██╔══██║               
                  ██████╔╝██║ ╚████║██║  ██║               
                  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝               
                                                            
                Sistema Biologico 2.0                      
""", style="cyan"), title="TradingDNA 2.0", border_style="cyan")
    console.print(logo)

def print_menu() -> Table:
    """Crea e restituisce la tabella del menu"""
    table = Table(show_header=False, border_style="cyan", box=None)
    table.add_column("Option", style="cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("[1]", "🧬 Sistema DNA         - Gestione strategie trading")
    table.add_row("[2]", "🛡️ Sistema Immunitario - Gestione rischi")
    table.add_row("[3]", "⚡ Metabolismo        - Gestione capitale")
    table.add_row("[4]", "🧠 Sistema Nervoso    - Analisi dati real-time")
    table.add_row("[5]", "🔄 Sistema Endocrino  - Adattamento parametri")
    table.add_row("[6]", "🧪 Sistema Riprod.    - Evoluzione strategie")
    table.add_row("", "")
    table.add_row("[7]", "⚙️  Configurazione     - Gestione impostazioni")
    table.add_row("[8]", "📥 Download Dati      - Scarica dati mercato")
    table.add_row("[9]", "📊 Log & Monitor      - Visualizza stato sistema")
    table.add_row("", "")
    table.add_row("[0]", "🚪 Esci")
    
    return table

def show_progress(description: str, total: int = 100) -> Progress:
    """Crea e restituisce una barra di progresso"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="cyan"),
        TaskProgressColumn(),
        console=console
    )

def handle_menu():
    """Gestisce l'interfaccia menu"""
    while True:
        print_ascii_logo()
        console.print(print_menu())
        choice = console.input("\nSeleziona un'opzione [cyan][0-9][/]: ")
        
        if choice == '0':
            with show_progress("Chiusura sistema") as progress:
                task = progress.add_task("Chiusura...", total=100)
                for _ in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.01)
            break
            
        valid_choices = {
            '1': ("Sistema DNA", handle_dna),
            '2': ("Sistema Immunitario", handle_immune),
            '3': ("Metabolismo", handle_metabolism),
            '4': ("Sistema Nervoso", handle_nervous),
            '5': ("Sistema Endocrino", handle_endocrine),
            '6': ("Sistema Riproduttivo", handle_reproductive),
            '7': ("Configurazione", lambda: handle_config(argparse.Namespace(action='show', file=None))),
            '8': ("Download Dati", lambda: handle_download(argparse.Namespace(dataset='all', pair=None, timeframe=None, progress=True))),
            '9': ("Log & Monitor", lambda: handle_log(argparse.Namespace(action='show', module=None)))
        }
        
        if choice in valid_choices:
            console.print(f"\nAvvio [cyan]{valid_choices[choice][0]}[/]...")
            with show_progress("Caricamento") as progress:
                task = progress.add_task("Inizializzazione...", total=100)
                for _ in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.01)
            try:
                valid_choices[choice][1]()
            except Exception as e:
                console.print(f"\n[red]Errore: {str(e)}[/]")
            console.input("\nPremi INVIO per continuare...")
        else:
            console.print("\n[red]Opzione non valida![/]")
            time.sleep(1)

def handle_dna():
    """Gestisce il Sistema DNA"""
    with show_progress("Sistema DNA") as progress:
        task = progress.add_task("Analisi strategie...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[yellow]Sistema DNA - Non ancora implementato[/]")

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

def setup_argparse() -> argparse.ArgumentParser:
    """Configura il parser degli argomenti CLI"""
    parser = argparse.ArgumentParser(
        description="TradingDNA 2.0 - Sistema di Trading Algoritmico Biologico",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Comandi principali
    subparsers = parser.add_subparsers(dest="command", help="Comandi disponibili")
    
    # Comando: menu
    menu_parser = subparsers.add_parser("menu", help="Mostra menu interattivo")
    
    # Comando: init
    init_parser = subparsers.add_parser("init", help="Inizializza il sistema")
    init_parser.add_argument("--force", action="store_true", help="Forza reinizializzazione")
    
    # Comando: config
    config_parser = subparsers.add_parser("config", help="Gestione configurazione")
    config_parser.add_argument("action", choices=["validate", "show"], help="Azione configurazione")
    config_parser.add_argument("--file", help="File di configurazione specifico")
    
    # Comando: download
    download_parser = subparsers.add_parser("download", help="Download dati mercato")
    download_parser.add_argument("--dataset", choices=["training", "testing", "paper_trading", "all"],
                               default="all", help="Dataset da scaricare")
    download_parser.add_argument("--pair", help="Coppia di trading (es. BTC/USDT)")
    download_parser.add_argument("--timeframe", help="Timeframe specifico")
    download_parser.add_argument("--progress", action="store_true", help="Mostra barra progresso")
    
    # Comando: log
    log_parser = subparsers.add_parser("log", help="Gestione logging")
    log_parser.add_argument("action", choices=["show", "clear", "test"], help="Azione logging")
    log_parser.add_argument("--module", help="Modulo specifico")
    
    return parser

def handle_init(args):
    """Gestisce il comando init"""
    try:
        initializer = Initializer(force=args.force)
        initializer.initialize()  # Chiamata una sola volta
        
        # Progress bar solo se l'inizializzazione ha successo
        with show_progress("Inizializzazione sistema") as progress:
            task = progress.add_task("Setup completato", total=100)
            progress.update(task, advance=100)  # Aggiorna subito al 100%
            
    except InitializationError as e:
        console.print(f"\n[red]Errore di inizializzazione: {str(e)}[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Errore: {str(e)}[/]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print(f"\n[yellow]Inizializzazione interrotta dall'utente[/]")
        sys.exit(1)

def handle_config(args):
    """Gestisce il comando config"""
    if args.action == "validate":
        with show_progress("Validazione configurazione") as progress:
            task = progress.add_task("Controllo...", total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                time.sleep(0.02)
        # TODO: Implementare validazione config
    elif args.action == "show":
        with show_progress("Caricamento configurazione") as progress:
            task = progress.add_task("Lettura...", total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                time.sleep(0.02)
        # TODO: Implementare visualizzazione config

def get_dataset_config(config: dict, dataset_name: str, pair: str = None, timeframe: str = None) -> list:
    """Estrae la configurazione del dataset specificato"""
    dataset = config['data'].get(dataset_name)
    if not dataset:
        return []
    
    pairs = dataset['pairs']
    if pair:
        pairs = [p for p in pairs if p['symbol'] == pair]
    
    result = []
    for p in pairs:
        timeframes = [timeframe] if timeframe else p['timeframes']
        for tf in timeframes:
            if tf in p['timeframes']:  # Verifica che il timeframe sia supportato
                result.append({
                    'symbol': p['symbol'],
                    'timeframe': tf,
                    'candles': p['candles']  # Usa il numero di candele invece delle date
                })
    return result

def handle_download(args):
    """Gestisce il comando download"""
    # Carica la configurazione DNA
    try:
        with open('config/dna.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Errore nel caricamento della configurazione DNA: {str(e)}[/]")
        return

    # Determina quali dataset scaricare
    datasets = ['training', 'testing', 'paper_trading'] if args.dataset == 'all' else [args.dataset]
    
    # Raccoglie tutte le serie da scaricare
    all_series = []
    for dataset_name in datasets:
        series = get_dataset_config(config, dataset_name, args.pair, args.timeframe)
        for s in series:
            s['dataset'] = dataset_name
        all_series.extend(series)

    if not all_series:
        console.print("[red]Nessuna serie temporale trovata per i criteri specificati[/]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="cyan"),
        TaskProgressColumn(),
        console=console
    ) as progress:
        # Task principale per il progresso totale
        total_task = progress.add_task("Download totale...", total=len(all_series))

        # Per ogni serie temporale
        for series in all_series:
            task_desc = f"Download {series['symbol']} ({series['timeframe']}) - {series['dataset']}"
            series_task = progress.add_task(task_desc, total=series['candles'])
            
            # Simula il download (TODO: implementare il download reale)
            for i in range(series['candles']):
                progress.update(series_task, advance=1)
                time.sleep(0.001)  # Ridotto il delay per non attendere troppo
            
            progress.update(total_task, advance=1)
            
            # Mostra info sul completamento
            console.print(f"[green]✓[/] {task_desc} completato")
            console.print(f"   Candele scaricate: {series['candles']}")

def handle_log(args):
    """Gestisce il comando log"""
    if args.action == "test":
        with show_progress("Test sistema logging") as progress:
            task = progress.add_task("Verifica...", total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                time.sleep(0.02)
        # TODO: Implementare test logging
    elif args.action == "show":
        with show_progress("Caricamento log") as progress:
            task = progress.add_task("Lettura...", total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                time.sleep(0.02)
        # TODO: Implementare visualizzazione log
    elif args.action == "clear":
        with show_progress("Pulizia log") as progress:
            task = progress.add_task("Cancellazione...", total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                time.sleep(0.02)
        # TODO: Implementare pulizia log

def main():
    """Funzione principale CLI"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging()
    
    # Gestione comando menu separatamente
    if args.command == "menu":
        handle_menu()
        return
    
    # Mapping altri comandi
    commands = {
        "init": handle_init,
        "config": handle_config,
        "download": handle_download,
        "log": handle_log
    }
    
    try:
        # Esegui comando
        commands[args.command](args)
    except KeyboardInterrupt:
        console.print("\n[red]Operazione interrotta[/]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Errore: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
