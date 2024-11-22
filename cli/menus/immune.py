"""Menu del Sistema Immunitario."""
import time
from typing import Dict
from rich.table import Table
from rich.console import Console

from cli.utils import show_progress, print_error
from cli.handlers.immune import ImmuneHandler

console = Console()

class ImmuneMenu:
    """Menu class for Immune System operations."""
    
    def __init__(self):
        """Initialize the immune system menu."""
        self.handler = ImmuneHandler()
    
    def display_menu(self) -> None:
        """Display the immune system menu options."""
        console.print("\n[cyan]Sistema Immunitario[/]")
        console.print(self._create_immune_menu())
    
    def handle_choice(self, choice: str) -> bool:
        """Handle menu choice and execute corresponding action."""
        if choice == "0":
            return False
            
        valid_choices = {
            '1': ("Analisi Rischi", self.handler.handle_risk),
            '2': ("Protezione Posizioni", self.handler.handle_protection),
            '3': ("Stato Exchange", self.handler.handle_exchange),
            '4': ("System Health", self.handler.handle_health),
            '5': ("Configurazione Protezioni", self._handle_protection_menu)
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
    
    def _create_immune_menu(self) -> Table:
        """Create and return the immune system menu table."""
        table = Table(show_header=False, border_style="cyan", box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        table.add_row("[1]", "🔍 Analisi Rischi     - Valutazione esposizione")
        table.add_row("[2]", "🛡️ Protezione Pos.   - Stop loss e take profit")
        table.add_row("[3]", "📊 Stato Exchange    - Monitoraggio exchange")
        table.add_row("[4]", "💉 System Health     - Stato sistema")
        table.add_row("[5]", "⚙️ Config. Protezioni - Gestione protezioni")
        table.add_row("", "")
        table.add_row("[0]", "⬅️  Torna al menu principale")
        
        return table
    
    def _create_protection_menu(self) -> Table:
        """Create and return the protection submenu table."""
        table = Table(show_header=False, border_style="cyan", box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        table.add_row("[1]", "🎯 Stop Loss Dinamici  - Gestione stop loss")
        table.add_row("[2]", "💰 Protezione Profitti - Take profit e trailing")
        table.add_row("[3]", "📊 Scaling Posizioni   - Gestione dimensione")
        table.add_row("[4]", "🌊 Adattamento Mercato - Adattamento condizioni")
        table.add_row("", "")
        table.add_row("[0]", "⬅️  Torna al menu immunitario")
        
        return table
    
    def _handle_protection_menu(self) -> None:
        """Handle protection submenu."""
        while True:
            console.print("\n[cyan]Configurazione Protezioni[/]")
            console.print(self._create_protection_menu())
            choice = console.input("\nSeleziona un'opzione [cyan][0-4][/]: ")
            
            if choice == '0':
                break
                
            valid_choices = {
                '1': ("Stop Loss Dinamici", 'dynamic_stops'),
                '2': ("Protezione Profitti", 'profit_protection'),
                '3': ("Scaling Posizioni", 'position_scaling'),
                '4': ("Adattamento Mercato", 'market_adaptation')
            }
            
            if choice in valid_choices:
                name, protection = valid_choices[choice]
                console.print(f"\nGestione [cyan]{name}[/]...")
                with show_progress("Caricamento") as progress:
                    task = progress.add_task("Inizializzazione...", total=100)
                    for _ in range(100):
                        progress.update(task, advance=1)
                        time.sleep(0.01)
                try:
                    self.handler.handle_protection_config(protection)
                except Exception as e:
                    print_error(f"Errore: {str(e)}")
                console.input("\nPremi INVIO per continuare...")
            else:
                console.print("\n[red]Opzione non valida![/]")
                time.sleep(1)
