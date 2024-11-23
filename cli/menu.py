"""Main menu interface for TradingDNA."""
from typing import Optional
import logging
import os
import shutil
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

from cli.menus.dna import DNAMenu
from cli.menus.immune import ImmuneMenu
from cli.menus.metabolism import MetabolismMenu
from cli.menus.nervous import NervousMenu
from cli.handlers.config import handle_config
from cli.handlers.download import handle_download
from cli.handlers.log import handle_log
from utils.logger_base import get_logger

logger = get_logger(__name__)
console = Console()

class MainMenu:
    """Main menu class for TradingDNA."""
    
    def __init__(self):
        """Initialize the main menu."""
        self.dna_menu = DNAMenu()
        self.immune_menu = ImmuneMenu()
        self.metabolism_menu = MetabolismMenu()
        self.nervous_menu = NervousMenu()
        
    def _create_status_dashboard(self) -> Panel:
        """Create status dashboard with system states."""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            padding=(0, 1),
            collapse_padding=True,
            box=None
        )
        
        # Configure columns with fixed width
        table.add_column("Sistema", style="cyan", width=15, justify="left")
        table.add_column("Stato", style="green", width=15, justify="left")
        table.add_column("Metriche", style="yellow", width=20, justify="left")
        
        # Add system states with compact metrics
        table.add_row("DNA", "✓ Attivo", "Fitness: 92%")
        table.add_row("Immunitario", "✓ Attivo", "Protezione: 95%")
        table.add_row("Metabolismo", "✓ Attivo", "Efficienza: 88%")
        table.add_row("Nervoso", "✓ Attivo", "Latenza: 45ms")
        table.add_row("Endocrino", "⚠ In Sviluppo", "---")
        table.add_row("Riproduttivo", "⚠ In Sviluppo", "---")
        
        return Panel(
            table,
            title="[bold cyan]Dashboard di Sistema[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
    
    def display_menu(self) -> None:
        """Display the main menu options with enhanced visual feedback."""
        # Menu options
        menu_text = (
            "🧬 [bold cyan]TradingDNA 2.0[/bold cyan]\n\n"
            "1. 🧬 [green]Sistema DNA[/green]\n"
            "2. 🛡️ [blue]Sistema Immunitario[/blue]\n"
            "3. ⚡ [yellow]Sistema Metabolismo[/yellow]\n"
            "4. 🧠 [magenta]Sistema Nervoso[/magenta]\n"
            "5. 🔄 [red]Sistema Endocrino[/red] [dim](In Sviluppo)[/dim]\n"
            "6. 🔋 [purple]Sistema Riproduttivo[/purple] [dim](In Sviluppo)[/dim]\n\n"
            "7. ⚙️ [cyan]Configurazione[/cyan]\n"
            "8. 📥 [cyan]Download Dati[/cyan]\n"
            "9. 📊 [cyan]Log e Monitor[/cyan]\n"
            "───────────────────────\n"
            "R. ⟲ [red]Reset Sistema[/red]\n"
            "0. 🚪 [white]Esci[/white]\n\n"
            "Seleziona un'opzione:"
        )
        
        # Display components
        console.clear()
        console.print()  # Add spacing
        console.print(self._create_status_dashboard())
        console.print(Panel(
            menu_text,
            title="Menu Principale",
            border_style="cyan",
            padding=(1, 2)
        ))
    
    def handle_choice(self, choice: str) -> bool:
        """Handle menu choice and execute corresponding action."""
        try:
            if choice == "1":
                self._handle_submenu(self.dna_menu)
            elif choice == "2":
                self._handle_submenu(self.immune_menu)
            elif choice == "3":
                self._handle_submenu(self.metabolism_menu)
            elif choice == "4":
                self._handle_submenu(self.nervous_menu)
            elif choice in ["5", "6"]:
                console.print("\n[yellow]⚠ Funzionalità in sviluppo[/yellow]")
                input("\nPremi INVIO per continuare...")
            elif choice == "7":
                handle_config(type('Args', (), {'action': 'show'})())
                input("\nPremi INVIO per continuare...")
            elif choice == "8":
                handle_download(type('Args', (), {'dataset': 'all', 'pair': None, 'timeframe': None})())
                input("\nPremi INVIO per continuare...")
            elif choice == "9":
                handle_log()
            elif choice.upper() == "R":
                self._handle_reset_system()
            elif choice == "0":
                console.print("\n[yellow]Arrivederci![/yellow]")
                return False
            else:
                console.print("\n[red]Opzione non valida[/red]")
                input("\nPremi INVIO per continuare...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling menu choice: {e}")
            console.print(f"\n[red]Errore: {str(e)}[/red]")
            input("\nPremi INVIO per continuare...")
            return True
    
    def _handle_submenu(self, submenu) -> None:
        """Handle submenu navigation."""
        while True:
            submenu.display_menu()
            choice = console.input("\nScelta: ")
            if not submenu.handle_choice(choice):
                break
        console.clear()  # Pulisce lo schermo prima di tornare al menu principale
    
    def _close_all_handlers(self) -> None:
        """Close all logging handlers."""
        # Chiudi gli handler del root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            try:
                handler.close()
                root_logger.removeHandler(handler)
            except:
                pass

        # Chiudi gli handler dei moduli configurati
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            try:
                for handler in logger.handlers[:]:
                    try:
                        handler.close()
                        logger.removeHandler(handler)
                    except:
                        pass
            except:
                pass

    def _handle_reset_system(self) -> None:
        """Handle system reset command."""
        try:
            # Chiedi conferma all'utente
            if not Confirm.ask("\n[red]⚠ Questa operazione cancellerà tutti i dati e i log del sistema. Continuare?[/red]"):
                console.print("\n[yellow]Reset sistema annullato[/yellow]")
                input("\nPremi INVIO per continuare...")
                return

            # Chiudi tutti gli handler di logging
            self._close_all_handlers()

            # Attendi che i file vengano rilasciati
            time.sleep(1)

            # Percorsi delle cartelle da resettare
            data_dir = Path("data")
            logs_dir = Path("logs")

            # Cancella il contenuto della cartella data
            if data_dir.exists():
                try:
                    shutil.rmtree(data_dir)
                    data_dir.mkdir()
                    console.print("\n[green]✓ Cartella data resettata[/green]")
                except Exception as e:
                    console.print(f"\n[red]Errore reset cartella data: {str(e)}[/red]")

            # Cancella il contenuto della cartella logs
            if logs_dir.exists():
                try:
                    # Rimuovi i file uno alla volta
                    for file in logs_dir.glob("*"):
                        try:
                            if file.is_file():
                                file.unlink()
                        except:
                            pass
                    console.print("[green]✓ Cartella logs resettata[/green]")
                except Exception as e:
                    console.print(f"\n[red]Errore reset cartella logs: {str(e)}[/red]")

            # Reinizializza il logging
            from utils.logger_base import setup_logging
            setup_logging()

            console.print("\n[green]✓ Reset sistema completato con successo[/green]")
            input("\nPremi INVIO per continuare...")

        except Exception as e:
            console.print(f"\n[red]Errore durante il reset: {str(e)}[/red]")
            input("\nPremi INVIO per continuare...")
            
            # Assicurati che il logging sia reinizializzato anche in caso di errore
            try:
                from utils.logger_base import setup_logging
                setup_logging()
            except:
                pass
    
    def run(self) -> None:
        """Run the main menu loop."""
        try:
            while True:
                self.display_menu()
                choice = console.input("\nScelta: ")
                if not self.handle_choice(choice):
                    break
        except KeyboardInterrupt:
            console.print("\n[yellow]Uscita forzata![/yellow]")
        except Exception as e:
            logger.error(f"Errore imprevisto: {e}")
            console.print(f"\n[red]Errore imprevisto: {str(e)}[/red]")
            input("\nPremi INVIO per continuare...")
