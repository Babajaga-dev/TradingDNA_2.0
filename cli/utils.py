"""
Funzioni di utilità per la CLI
"""
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text

# Console per output formattato
console = Console()

def print_ascii_logo():
    """Stampa il logo ASCII di TradingDNA 2.0"""
    logo = Panel(Text("""
████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗     
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝     
   ██║   ██████╔╝███████║██║  ██║██║██║╚██╗██║██║  ███╗    
   ██║   ██╔══██╗██╔══██║██║  ██║██║██║ ╚████║██║   ██║    
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

def show_progress(description: str, total: int = 100) -> Progress:
    """Crea e restituisce una barra di progresso"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="cyan"),
        TaskProgressColumn(),
        console=console
    )

def create_progress() -> Progress:
    """Crea una barra di progresso per il download"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="cyan"),
        TaskProgressColumn(),
        console=console
    )

def print_error(message: str):
    """Stampa un messaggio di errore"""
    console.print(f"[red]✗[/] {message}")

def print_success(message: str):
    """Stampa un messaggio di successo"""
    console.print(f"[green]✓[/] {message}")
