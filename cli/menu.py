"""
Gestione menu CLI
"""
import time
import argparse
from rich.table import Table

from cli.utils import console, show_progress, print_ascii_logo, print_error

def print_dna_submenu() -> Table:
    """Crea e restituisce la tabella del submenu DNA"""
    table = Table(show_header=False, border_style="cyan", box=None)
    table.add_column("Option", style="cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("[1]", "🧬 Inizializza DNA    - Setup sistema DNA")
    table.add_row("[2]", "📊 Analisi Pattern    - Pattern Recognition")
    table.add_row("[3]", "📈 Indicatori        - Analisi tecnica")
    table.add_row("[4]", "🎯 Scoring           - Performance DNA")
    table.add_row("", "")
    table.add_row("[0]", "⬅️  Torna al menu principale")
    
    return table

def handle_dna_menu(commands: dict):
    """Gestisce il submenu DNA"""
    while True:
        console.print("\n[cyan]Sistema DNA[/]")
        console.print(print_dna_submenu())
        choice = console.input("\nSeleziona un'opzione [cyan][0-4][/]: ")
        
        if choice == '0':
            break
            
        valid_choices = {
            '1': ("Inizializzazione DNA", lambda: commands["dna"](argparse.Namespace(action='init'))),
            '2': ("Analisi Pattern", lambda: commands["dna"](argparse.Namespace(action='analyze', pair=None, timeframe=None))),
            '3': ("Indicatori Tecnici", lambda: commands["dna"](argparse.Namespace(action='indicators', pair=None, timeframe=None))),
            '4': ("DNA Scoring", lambda: commands["dna"](argparse.Namespace(action='score')))
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
                print_error(f"Errore: {str(e)}")
            console.input("\nPremi INVIO per continuare...")
        else:
            console.print("\n[red]Opzione non valida![/]")
            time.sleep(1)

def print_menu() -> Table:
    """Crea e restituisce la tabella del menu principale"""
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

def handle_menu(commands: dict):
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
            '1': ("Sistema DNA", lambda: handle_dna_menu(commands)),
            '2': ("Sistema Immunitario", commands["immune"]),
            '3': ("Metabolismo", commands["metabolism"]),
            '4': ("Sistema Nervoso", commands["nervous"]),
            '5': ("Sistema Endocrino", commands["endocrine"]),
            '6': ("Sistema Riproduttivo", commands["reproductive"]),
            '7': ("Configurazione", lambda: commands["config"](argparse.Namespace(action='show', file=None))),
            '8': ("Download Dati", lambda: commands["download"](argparse.Namespace(dataset='all', pair=None, timeframe=None, progress=True))),
            '9': ("Log & Monitor", lambda: commands["log"](argparse.Namespace(action='show', module=None)))
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
                print_error(f"Errore: {str(e)}")
            console.input("\nPremi INVIO per continuare...")
        else:
            console.print("\n[red]Opzione non valida![/]")
            time.sleep(1)
