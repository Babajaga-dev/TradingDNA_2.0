"""Menu interface for the Nervous System."""
from typing import Dict, Optional
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.align import Align

from cli.handlers.nervous import NervousHandler
from utils.logger_base import get_logger

logger = get_logger(__name__)
console = Console()

class NervousMenu:
    """Menu class for Nervous System operations."""
    
    def __init__(self):
        """Initialize the nervous system menu."""
        self.handler = NervousHandler()
        
    def display_menu(self) -> None:
        """Display the nervous system menu options."""
        menu = """
🧠 Sistema Nervoso

1. Stato Sistema
2. Metriche Performance
3. Pattern Attivi
4. Gestione Stream
5. Ottimizzazione
0. Indietro

Seleziona un'opzione: """
        
        console.print(Panel(menu, title="Menu Sistema Nervoso", border_style="blue"))
    
    def handle_choice(self, choice: str) -> bool:
        """Handle menu choice and execute corresponding action."""
        try:
            if choice == "1":
                self._show_system_status()
            elif choice == "2":
                self._show_performance_metrics()
            elif choice == "3":
                self._show_active_patterns()
            elif choice == "4":
                self._show_stream_menu()
            elif choice == "5":
                self._optimize_system()
            elif choice == "0":
                return False
            else:
                console.print("[red]Opzione non valida[/red]")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling menu choice: {e}")
            console.print(f"[red]Errore: {str(e)}[/red]")
            return True
    
    def _show_system_status(self) -> None:
        """Display system status information."""
        result = self.handler.get_system_status()
        
        if result['status'] == 'error':
            console.print(f"[red]Errore: {result['message']}[/red]")
            return
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="health"),
            Layout(name="streaming", size=3),
            Layout(name="metrics"),
            Layout(name="config")
        )
        
        # Health score panel
        health_score = result['health']
        health_color = "green" if health_score > 0.85 else "yellow" if health_score > 0.7 else "red"
        health_panel = Panel(
            f"Score: [bold {health_color}]{health_score:.2f}[/bold {health_color}]",
            title="Stato Sistema",
            border_style=health_color
        )
        layout["health"].update(health_panel)
        
        # Streaming status panel
        if 'streaming' in result:
            stream_info = result['streaming']
            stream_text = (
                f"[green]✓ Attivo[/green]\n"
                f"Symbol: {stream_info['symbol']}\n"
                f"Timeframe: {stream_info['timeframe']}\n"
                f"Velocità: {stream_info['speed']}x"
            )
        else:
            stream_text = "[red]✗ Inattivo[/red]"
        
        layout["streaming"].update(Panel(stream_text, title="Stato Streaming"))
        
        # Metrics table
        metrics_table = Table(title="Metriche Performance")
        metrics_table.add_column("Metrica", style="cyan")
        metrics_table.add_column("Valore", style="magenta")
        metrics_table.add_column("Range Ottimale", style="green")
        
        for name, data in result['metrics'].items():
            metrics_table.add_row(
                data['description'],
                f"{data['value']:.2f}",
                data['optimal_range']
            )
        
        layout["metrics"].update(metrics_table)
        
        # Config panel
        config_text = "\n".join([
            f"[cyan]Preprocessing:[/cyan] {result['config']['preprocessing']}",
            f"[cyan]Pattern Recognition:[/cyan] {result['config']['patterns']}",
            f"[cyan]Performance:[/cyan] {result['config']['performance']}"
        ])
        layout["config"].update(Panel(config_text, title="Configurazione"))
        
        console.print(layout)
    
    def _show_performance_metrics(self) -> None:
        """Display detailed performance metrics."""
        result = self.handler.get_performance_metrics()
        
        if result['status'] == 'error':
            console.print(f"[red]Errore: {result['message']}[/red]")
            return
        
        table = Table(title="Metriche Dettagliate")
        table.add_column("Metrica", style="cyan")
        table.add_column("Valore", style="magenta")
        table.add_column("Range Ottimale", style="green")
        table.add_column("Descrizione", style="yellow")
        
        for name, data in result['metrics'].items():
            table.add_row(
                name,
                f"{data['value']:.2f}",
                data['optimal_range'],
                data['description']
            )
        
        console.print(table)
    
    def _show_active_patterns(self) -> None:
        """Display currently active market patterns."""
        result = self.handler.get_active_patterns()
        
        if result['status'] == 'error':
            console.print(f"[red]Errore: {result['message']}[/red]")
            return
        
        if not result['patterns']:
            console.print("[yellow]Nessun pattern attivo al momento[/yellow]")
            return
        
        table = Table(title="Pattern Attivi")
        table.add_column("Pattern", style="cyan")
        table.add_column("Confidenza", style="magenta")
        table.add_column("Timeframe", style="yellow")
        
        for pattern in result['patterns']:
            table.add_row(
                pattern['name'],
                f"{pattern['confidence']:.2f}",
                pattern['timeframe']
            )
        
        console.print(table)
    
    def _show_stream_menu(self) -> None:
        """Display stream management submenu."""
        menu = """
1. Avvia Stream
2. Ferma Stream
3. Configura Timeframe
4. Configura Velocità
5. Lista Pair Disponibili
0. Indietro

Seleziona un'opzione: """
        
        while True:
            console.print(Panel(menu, title="Gestione Stream", border_style="blue"))
            choice = console.input("Scelta: ")
            
            if choice == "1":
                # Get available pairs
                pairs = self.handler.get_available_pairs()
                if pairs['status'] == 'error':
                    console.print(f"[red]{pairs['message']}[/red]")
                    continue
                
                # Show pairs table
                table = Table(title="Pair Disponibili")
                table.add_column("Symbol", style="cyan")
                for pair in pairs['pairs']:
                    table.add_row(pair)
                console.print(table)
                
                # Get symbol choice
                symbol = console.input("\nInserisci il symbol: ")
                if symbol not in pairs['pairs']:
                    console.print("[red]Symbol non valido[/red]")
                    continue
                
                result = self.handler.start_data_stream(symbol)
                console.print(
                    f"[green]{result['message']}[/green]" 
                    if result['status'] == 'success' 
                    else f"[red]{result['message']}[/red]"
                )
                
            elif choice == "2":
                result = self.handler.stop_data_stream()
                console.print(
                    f"[green]{result['message']}[/green]" 
                    if result['status'] == 'success' 
                    else f"[red]{result['message']}[/red]"
                )
                
            elif choice == "3":
                # Get available timeframes
                timeframes = self.handler.get_available_timeframes()
                if timeframes['status'] == 'error':
                    console.print(f"[red]{timeframes['message']}[/red]")
                    continue
                
                # Show timeframes table
                table = Table(title="Timeframe Disponibili")
                table.add_column("Timeframe", style="cyan")
                for tf in timeframes['timeframes']:
                    table.add_row(tf)
                console.print(table)
                
                # Get timeframe choice
                timeframe = console.input("\nInserisci il timeframe: ")
                if timeframe not in timeframes['timeframes']:
                    console.print("[red]Timeframe non valido[/red]")
                    continue
                
                result = self.handler.set_timeframe(timeframe)
                console.print(
                    f"[green]{result['message']}[/green]" 
                    if result['status'] == 'success' 
                    else f"[red]{result['message']}[/red]"
                )
                
            elif choice == "4":
                speed = console.input("\nInserisci la velocità di simulazione (es. 1.0 = tempo reale): ")
                try:
                    speed = float(speed)
                    result = self.handler.set_simulation_speed(speed)
                    console.print(
                        f"[green]{result['message']}[/green]" 
                        if result['status'] == 'success' 
                        else f"[red]{result['message']}[/red]"
                    )
                except ValueError:
                    console.print("[red]Velocità non valida[/red]")
                
            elif choice == "5":
                pairs = self.handler.get_available_pairs()
                if pairs['status'] == 'error':
                    console.print(f"[red]{pairs['message']}[/red]")
                    continue
                
                table = Table(title="Pair Disponibili")
                table.add_column("Symbol", style="cyan")
                for pair in pairs['pairs']:
                    table.add_row(pair)
                console.print(table)
                
            elif choice == "0":
                break
            else:
                console.print("[red]Opzione non valida[/red]")
    
    def _optimize_system(self) -> None:
        """Run system optimization."""
        console.print("[yellow]Avvio ottimizzazione parametri...[/yellow]")
        
        result = self.handler.optimize_parameters()
        
        if result['status'] == 'error':
            console.print(f"[red]Errore: {result['message']}[/red]")
            return
        
        console.print(f"[green]{result['message']}[/green]")
