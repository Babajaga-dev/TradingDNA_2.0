"""Menu del Sistema DNA."""
import time
import argparse
from typing import Dict
from rich.table import Table
from rich.console import Console

from cli.utils import show_progress, print_error
from cli.handlers.dna import DNAMainHandler  # Modificato: uso DNAMainHandler invece di DNAHandler

console = Console()

class DNAMenu:
    """Menu class for DNA System operations."""
    
    def __init__(self):
        """Initialize the DNA menu."""
        self.handler = DNAMainHandler()  # Modificato: inizializzo DNAMainHandler
    
    def display_menu(self) -> None:
        """Display the DNA menu options."""
        console.print("\n[cyan]Sistema DNA[/]")
        console.print(self._create_dna_menu())
    
    def handle_choice(self, choice: str) -> bool:
        """Handle menu choice and execute corresponding action."""
        if choice == "0":
            return False
            
        valid_choices = {
            '1': ("Inizializzazione DNA", self._handle_init),
            '2': ("Gestione Geni", self._handle_genes),
            '3': ("Ottimizzazione", self._handle_optimization),
            '4': ("Validazione", self._handle_validation),
            '5': ("Composizione", self._handle_composition),
            '6': ("Analisi Pattern", self._handle_pattern_analysis),
            '7': ("Indicatori Tecnici", self._handle_indicators),
            '8': ("DNA Scoring", self._handle_scoring),
            '9': ("Backtest", self._handle_backtest),
            '10': ("Configurazione", self._handle_config)
        }
        
        if choice in valid_choices:
            name, handler = valid_choices[choice]
            console.print(f"\nAvvio [cyan]{name}[/]...")
            with show_progress("Caricamento") as progress:
                task = progress.add_task("Inizializzazione...", total=100)
                for _ in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.01)
            try:
                handler()
            except Exception as e:
                print_error(f"Errore: {str(e)}")
            console.input("\nPremi INVIO per continuare...")
            return True
        else:
            console.print("\n[red]Opzione non valida![/]")
            time.sleep(1)
            return True
    
    def _create_dna_menu(self) -> Table:
        """Create and return the DNA menu table."""
        table = Table(show_header=False, border_style="cyan", box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        table.add_row("[1]", "🧬 Inizializza DNA    - Setup sistema DNA")
        table.add_row("[2]", "📊 Gestione Geni     - RSI, MACD, Bollinger, Volume")
        table.add_row("[3]", "🎯 Ottimizzazione    - Ottimizza parametri")
        table.add_row("[4]", "📈 Validazione       - Test strategia")
        table.add_row("[5]", "🔄 Composizione      - Genera segnali")
        table.add_row("[6]", "📊 Analisi Pattern   - Pattern Recognition")
        table.add_row("[7]", "📉 Indicatori       - Analisi tecnica")
        table.add_row("[8]", "🎯 Scoring          - Performance DNA")
        table.add_row("[9]", "📊 Backtest         - Test storico")
        table.add_row("[10]", "⚙️  Configurazione   - Parametri sistema")
        table.add_row("", "")
        table.add_row("[0]", "⬅️  Torna al menu principale")
        
        return table
    
    def _create_genes_menu(self) -> Table:
        """Create and return the genes submenu table."""
        table = Table(show_header=False, border_style="cyan", box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        table.add_row("[1]", "📊 RSI              - Relative Strength Index")
        table.add_row("[2]", "📈 MACD             - Moving Average Convergence Divergence")
        table.add_row("[3]", "📉 Bollinger        - Bollinger Bands")
        table.add_row("[4]", "📊 Volume           - Volume Analysis")
        table.add_row("", "")
        table.add_row("[0]", "⬅️  Torna al menu DNA")
        
        return table
    
    def _handle_genes(self) -> None:
        """Handle genes submenu."""
        while True:
            console.print("\n[cyan]Gestione Geni[/]")
            console.print(self._create_genes_menu())
            choice = console.input("\nSeleziona un'opzione [cyan][0-4][/]: ")
            
            if choice == '0':
                break
                
            valid_choices = {
                '1': ("RSI", lambda: self.handler.handle_gene('rsi')),
                '2': ("MACD", lambda: self.handler.handle_gene('macd')),
                '3': ("Bollinger", lambda: self.handler.handle_gene('bollinger')),
                '4': ("Volume", lambda: self.handler.handle_gene('volume'))
            }
            
            if choice in valid_choices:
                name, handler = valid_choices[choice]
                console.print(f"\nAvvio [cyan]{name}[/]...")
                with show_progress("Caricamento") as progress:
                    task = progress.add_task("Inizializzazione...", total=100)
                    for _ in range(100):
                        progress.update(task, advance=1)
                        time.sleep(0.01)
                try:
                    handler()
                except Exception as e:
                    print_error(f"Errore: {str(e)}")
                console.input("\nPremi INVIO per continuare...")
            else:
                console.print("\n[red]Opzione non valida![/]")
                time.sleep(1)
    
    def _handle_init(self) -> None:
        """Handle DNA initialization."""
        self.handler.handle_init()
    
    def _handle_optimization(self) -> None:
        """Handle DNA optimization."""
        self.handler.handle_optimization()
    
    def _handle_validation(self) -> None:
        """Handle DNA validation."""
        self.handler.handle_validation()
    
    def _handle_composition(self) -> None:
        """Handle DNA composition."""
        self.handler.handle_composition()
    
    def _handle_pattern_analysis(self) -> None:
        """Handle pattern analysis."""
        self.handler.handle_pattern_analysis()
    
    def _handle_indicators(self) -> None:
        """Handle technical indicators."""
        self.handler.handle_indicators()
    
    def _handle_scoring(self) -> None:
        """Handle DNA scoring."""
        self.handler.handle_scoring()
        
    def _handle_backtest(self) -> None:
        """Handle DNA backtest."""
        self.handler.handle_backtest()
        
    def _handle_config(self) -> None:
        """Handle DNA configuration."""
        self.handler.handle_config()