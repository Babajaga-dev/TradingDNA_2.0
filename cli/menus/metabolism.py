"""Menu del Sistema Metabolico."""
import time
from typing import Dict
from rich.table import Table
from rich.console import Console

from cli.utils import show_progress, print_error
from cli.handlers.metabolism import MetabolismHandler

console = Console()

class MetabolismMenu:
    """Menu class for Metabolism System operations."""
    
    def __init__(self):
        """Initialize the metabolism menu."""
        self.handler = MetabolismHandler()
    
    def display_menu(self) -> None:
        """Display the metabolism menu options."""
        console.print("\n[cyan]Sistema Metabolico[/]")
        console.print(self._create_metabolism_menu())
    
    def handle_choice(self, choice: str) -> bool:
        """Handle menu choice and execute corresponding action."""
        if choice == "0":
            return False
            
        valid_choices = {
            '1': ("Gestione Capitale", self._handle_capital_menu),
            '2': ("Dimensionamento", self.handler.handle_position_sizing),
            '3': ("Performance", self.handler.handle_performance),
            '4': ("Configurazione", self.handler.handle_config),
            '5': ("Risk Management", self.handler.handle_risk_budget)
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
    
    def _create_metabolism_menu(self) -> Table:
        """Create and return the metabolism menu table."""
        table = Table(show_header=False, border_style="cyan", box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        table.add_row("[1]", "💰 Gestione Capitale  - Allocazione e budgeting")
        table.add_row("[2]", "📊 Dimensionamento    - Sizing posizioni")
        table.add_row("[3]", "📈 Performance       - Monitoraggio metriche")
        table.add_row("[4]", "⚙️  Configurazione    - Parametri sistema")
        table.add_row("[5]", "🔄 Risk Management   - Gestione rischio")
        table.add_row("", "")
        table.add_row("[0]", "⬅️  Torna al menu principale")
        
        return table
    
    def _create_capital_menu(self) -> Table:
        """Create and return the capital management submenu table."""
        table = Table(show_header=False, border_style="cyan", box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        table.add_row("[1]", "💼 Portfolio         - Gestione portfolio")
        table.add_row("[2]", "📊 Allocazione       - Allocazione capitale")
        table.add_row("[3]", "⚖️  Risk Budget       - Budget per strategia")
        table.add_row("[4]", "📈 Performance       - Tracking capitale")
        table.add_row("", "")
        table.add_row("[0]", "⬅️  Torna al menu metabolismo")
        
        return table
    
    def _handle_capital_menu(self) -> None:
        """Handle capital management submenu."""
        while True:
            console.print("\n[cyan]Gestione Capitale[/]")
            console.print(self._create_capital_menu())
            choice = console.input("\nSeleziona un'opzione [cyan][0-4][/]: ")
            
            if choice == '0':
                break
                
            valid_choices = {
                '1': ("Portfolio", self.handler.handle_portfolio),
                '2': ("Allocazione", self.handler.handle_allocation),
                '3': ("Risk Budget", self.handler.handle_risk_budget),
                '4': ("Performance", self.handler.handle_performance)
            }
            
            if choice in valid_choices:
                name, handler = valid_choices[choice]
                console.print(f"\nGestione [cyan]{name}[/]...")
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
