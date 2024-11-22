"""Handler per i comandi del Sistema Metabolico."""
from decimal import Decimal
from typing import Optional
from rich.table import Table
from rich.console import Console

from utils.logger_base import get_logger
from utils.config import ConfigManager
from core.metabolism.capital_manager import CapitalManager
from core.metabolism.position_sizer import PositionSizer, PositionConfig
from core.metabolism.performance_tracker import PerformanceTracker
from cli.utils import show_progress, print_error

console = Console()
logger = get_logger(__name__)

class MetabolismHandler:
    """Handler class for Metabolism System operations."""
    
    def __init__(self):
        """Initialize the metabolism handler."""
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config('metabolism')
        
        # Initialize components
        self.capital_manager = CapitalManager(
            initial_capital=Decimal(str(self.config['capital_manager']['initial_capital'])),
            risk_limit=self.config['capital_manager']['risk_limit']
        )
        
        position_config = PositionConfig(
            max_position_size=Decimal(str(self.config['position_sizer']['max_position_size'])),
            risk_per_trade=self.config['position_sizer']['risk_per_trade'],
            stop_loss_pct=self.config['position_sizer']['stop_loss_pct'],
            max_exposure_pct=self.config['position_sizer']['max_exposure_pct']
        )
        self.position_sizer = PositionSizer(position_config)
        
        self.performance_tracker = PerformanceTracker(
            initial_capital=Decimal(str(self.config['capital_manager']['initial_capital']))
        )
    
    def handle_portfolio(self) -> None:
        """Handle portfolio visualization."""
        try:
            table = Table(title="Portfolio Overview")
            table.add_column("Strategy", style="cyan")
            table.add_column("Capital", style="green")
            table.add_column("Risk Budget", style="yellow")
            
            summary = self.capital_manager.get_allocation_summary()
            for strategy_id, data in summary.items():
                table.add_row(
                    strategy_id,
                    f"${float(data['capital']):,.2f}",
                    f"{data['risk_budget']*100:.1f}%"
                )
                
            console.print(table)
        except Exception as e:
            logger.error(f"Error handling portfolio: {str(e)}")
            print_error(str(e))
            raise
    
    def handle_allocation(self, strategy_id: Optional[str] = None, amount: Optional[float] = None) -> None:
        """Handle capital allocation."""
        try:
            if not strategy_id:
                strategy_id = console.input("Inserisci ID strategia: ")
            if not amount:
                amount = float(console.input("Inserisci importo da allocare: $"))
                
            success = self.capital_manager.allocate_capital(
                strategy_id,
                Decimal(str(amount))
            )
            
            if success:
                console.print(f"[green]Allocati ${amount:,.2f} alla strategia {strategy_id}[/]")
            else:
                console.print("[red]Allocazione fallita - fondi insufficienti[/]")
        except Exception as e:
            logger.error(f"Error handling allocation: {str(e)}")
            print_error(str(e))
            raise
    
    def handle_risk_budget(self, strategy_id: Optional[str] = None, risk_pct: Optional[float] = None) -> None:
        """Handle risk budget management."""
        try:
            if not strategy_id:
                strategy_id = console.input("Inserisci ID strategia: ")
            if not risk_pct:
                risk_pct = float(console.input("Inserisci percentuale rischio (0-100): ")) / 100
                
            success = self.capital_manager.set_risk_budget(strategy_id, risk_pct)
            
            if success:
                console.print(f"[green]Risk budget {risk_pct*100:.1f}% impostato per {strategy_id}[/]")
            else:
                console.print("[red]Impossibile impostare risk budget - limite superato[/]")
        except Exception as e:
            logger.error(f"Error handling risk budget: {str(e)}")
            print_error(str(e))
            raise
    
    def handle_performance(self) -> None:
        """Handle performance metrics visualization."""
        try:
            metrics = self.performance_tracker.get_performance_metrics()
            
            table = Table(title="Performance Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total P&L", f"${float(metrics.total_pnl):,.2f}")
            table.add_row("ROI", f"{metrics.total_roi*100:.2f}%")
            table.add_row("Max Drawdown", f"{metrics.max_drawdown*100:.2f}%")
            table.add_row("Win Rate", f"{metrics.win_rate*100:.1f}%")
            table.add_row("Win/Loss Ratio", f"{metrics.avg_win_loss_ratio:.2f}")
            table.add_row("Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}")
            table.add_row("Sortino Ratio", f"{metrics.sortino_ratio:.2f}")
            table.add_row("Avg Holding Time", f"{metrics.avg_holding_time:.1f}h")
            
            console.print(table)
        except Exception as e:
            logger.error(f"Error handling performance: {str(e)}")
            print_error(str(e))
            raise
    
    def handle_position_sizing(self, capital: Optional[float] = None, entry_price: Optional[float] = None) -> None:
        """Handle position sizing calculation."""
        try:
            if not capital:
                capital = float(console.input("Inserisci capitale disponibile: $"))
            if not entry_price:
                entry_price = float(console.input("Inserisci prezzo di entrata: $"))
                
            stop_loss = console.input("Inserisci prezzo stop loss (opzionale): $")
            stop_loss = float(stop_loss) if stop_loss else None
            
            signal_strength = float(console.input("Inserisci forza segnale (0-1): ") or "1.0")
            
            size, metrics = self.position_sizer.calculate_position_size(
                capital=Decimal(str(capital)),
                entry_price=Decimal(str(entry_price)),
                stop_loss=Decimal(str(stop_loss)) if stop_loss else None,
                signal_strength=signal_strength
            )
            
            table = Table(title="Position Sizing")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Position Size", f"{float(size):.4f}")
            table.add_row("Base Size", f"{float(metrics['base_size']):.4f}")
            table.add_row("Risk Amount", f"${float(metrics['risk_amount']):,.2f}")
            table.add_row("Signal Adjustment", f"{metrics['signal_adjustment']:.2f}")
            
            console.print(table)
        except Exception as e:
            logger.error(f"Error handling position sizing: {str(e)}")
            print_error(str(e))
            raise
    
    def handle_config(self) -> None:
        """Handle metabolism configuration visualization."""
        try:
            table = Table(title="Metabolism Configuration")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Description", style="white")
            
            # Capital Manager Config
            table.add_row(
                "initial_capital",
                f"${self.config['capital_manager']['initial_capital']:,.2f}",
                "Capitale iniziale"
            )
            table.add_row(
                "risk_limit",
                f"{self.config['capital_manager']['risk_limit']*100:.1f}%",
                "Limite rischio per trade"
            )
            
            # Position Sizer Config
            table.add_row(
                "max_position_size",
                f"${self.config['position_sizer']['max_position_size']:,.2f}",
                "Dimensione massima posizione"
            )
            table.add_row(
                "risk_per_trade",
                f"{self.config['position_sizer']['risk_per_trade']*100:.1f}%",
                "Rischio per trade"
            )
            
            console.print(table)
        except Exception as e:
            logger.error(f"Error handling config: {str(e)}")
            print_error(str(e))
            raise
