"""Handler per i comandi del sistema immunitario."""
from typing import Optional, Dict, Any
import time
import logging
from pathlib import Path
import pandas as pd
from rich.table import Table
from rich.panel import Panel
from rich.console import Group
from rich.prompt import Confirm

from cli.utils import show_progress, console, print_error, print_success
from utils.logger_base import get_component_logger
from utils.config import load_config
from core.immune_system import ImmuneSystem

# Setup logger
logger = get_component_logger('ImmuneHandler')

class ImmuneHandler:
    """Handler class for Immune System operations."""
    
    def __init__(self):
        """Initialize the immune system handler."""
        self.immune_system = ImmuneSystem()
        self.sample_positions = [
            {
                'symbol': 'BTC/USDT',
                'size': 1.0,
                'entry_price': 40000.0,
                'current_price': 41000.0,
                'unrealized_pnl': 1000.0,
                'exchange': 'binance',
                'volatility': 0.15
            },
            {
                'symbol': 'ETH/USDT',
                'size': 10.0,
                'entry_price': 2800.0,
                'current_price': 2900.0,
                'unrealized_pnl': 1000.0,
                'exchange': 'kraken',
                'volatility': 0.12
            }
        ]
        
        # Update exchange health metrics
        self.immune_system._exchange_health = {
            'binance': {
                'uptime': 0.99,
                'api_response_time': 100,
                'error_rate': 0.01
            },
            'kraken': {
                'uptime': 0.95,
                'api_response_time': 300,
                'error_rate': 0.05
            }
        }
    
    def show_protection_config(self) -> None:
        """Visualizza la configurazione delle protezioni."""
        try:
            config = self.immune_system.get_protection_config()
            
            config_table = Table(title="Configurazione Protezioni", border_style="cyan")
            config_table.add_column("Protezione", style="cyan")
            config_table.add_column("Stato", style="white", justify="center")
            
            config_table.add_row(
                "Stop Loss Dinamici",
                "✓ ON" if config['dynamic_stops'] else "✗ OFF"
            )
            config_table.add_row(
                "Protezione Profitti",
                "✓ ON" if config['profit_protection'] else "✗ OFF"
            )
            config_table.add_row(
                "Scaling Posizioni",
                "✓ ON" if config['position_scaling'] else "✗ OFF"
            )
            config_table.add_row(
                "Adattamento Mercato",
                "✓ ON" if config['market_adaptation'] else "✗ OFF"
            )
            
            console.print(config_table)
            
        except Exception as e:
            logger.error(f"Errore durante visualizzazione config protezioni: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def toggle_protection(self, protection_name: str) -> None:
        """
        Attiva/disattiva una protezione specifica.
        
        Args:
            protection_name: Nome della protezione da modificare
        """
        try:
            config = self.immune_system.get_protection_config()
            config[protection_name] = not config[protection_name]
            self.immune_system.set_protection_config(config)
            
            status = "attivata" if config[protection_name] else "disattivata"
            print_success(f"Protezione {protection_name} {status}")
            
        except Exception as e:
            logger.error(f"Errore durante modifica protezione: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def show_risk_analysis(self) -> None:
        """Visualizza l'analisi dei rischi correnti."""
        try:
            risk_metrics = self.immune_system.analyze_risk(self.sample_positions)
            
            metrics_table = Table(title="Metriche di Rischio", border_style="cyan")
            metrics_table.add_column("Metrica", style="cyan")
            metrics_table.add_column("Valore", style="white", justify="right")
            
            metrics_table.add_row(
                "Esposizione Totale",
                f"{risk_metrics.total_exposure*100:.1f}%"
            )
            metrics_table.add_row(
                "Drawdown",
                f"{risk_metrics.drawdown*100:.1f}%"
            )
            metrics_table.add_row(
                "Rischio Controparte",
                f"{risk_metrics.counterparty_risk*100:.1f}%"
            )
            metrics_table.add_row(
                "Correlazione Asset",
                f"{risk_metrics.asset_correlation*100:.1f}%"
            )
            
            console.print(metrics_table)
            
        except Exception as e:
            logger.error(f"Errore durante analisi rischi: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def show_position_protection(self) -> None:
        """Visualizza le protezioni delle posizioni."""
        try:
            protection_table = Table(
                title="Protezione Posizioni",
                border_style="cyan"
            )
            protection_table.add_column("Simbolo", style="cyan")
            protection_table.add_column("Prezzo", justify="right")
            protection_table.add_column("Stop Loss", justify="right")
            protection_table.add_column("Take Profit", justify="right")
            protection_table.add_column("Trailing Stop", justify="right")
            protection_table.add_column("Scale Out", justify="right")
            
            for position in self.sample_positions:
                protection = self.immune_system.get_position_protection(position)
                
                protection_table.add_row(
                    position['symbol'],
                    f"${position['current_price']:,.2f}",
                    f"${protection.get('stop_loss', 0):,.2f}",
                    f"${protection.get('take_profit', 0):,.2f}",
                    f"${protection.get('trailing_activation', 0):,.2f}",
                    f"${protection.get('scale_out_target', 0):,.2f}"
                )
                
            console.print(protection_table)
            
        except Exception as e:
            logger.error(f"Errore durante analisi protezioni: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def show_exchange_health(self) -> None:
        """Visualizza lo stato di salute degli exchange."""
        try:
            health_table = Table(title="Stato Exchange", border_style="cyan")
            health_table.add_column("Exchange", style="cyan")
            health_table.add_column("Uptime", justify="right")
            health_table.add_column("Latenza API", justify="right")
            health_table.add_column("Tasso Errori", justify="right")
            health_table.add_column("Score", justify="right")
            
            for exchange, metrics in self.immune_system._exchange_health.items():
                health_table.add_row(
                    exchange,
                    f"{metrics.get('uptime', 0.0)*100:.1f}%",
                    f"{metrics.get('api_response_time', 0):.0f}ms",
                    f"{metrics.get('error_rate', 0.0)*100:.1f}%",
                    f"{self.immune_system._get_exchange_health_score(exchange)*100:.1f}%"
                )
                
            console.print(health_table)
            
        except Exception as e:
            logger.error(f"Errore durante analisi exchange: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def show_system_health(self) -> None:
        """Visualizza lo stato di salute del sistema immunitario."""
        try:
            health = self.immune_system.get_system_health()
            
            health_table = Table(show_header=False, show_edge=False, box=None)
            health_table.add_column(justify="left")
            health_table.add_row(f"Risk Management: {health['risk_management']*100:.1f}%")
            health_table.add_row(f"Defense Efficiency: {health['defense_efficiency']*100:.1f}%")
            health_table.add_row(f"System Stability: {health['system_stability']*100:.1f}%")
            
            health_panel = Panel(
                health_table,
                title="System Health",
                border_style="cyan",
                padding=(1, 2)
            )
            
            console.print(health_panel)
            
        except Exception as e:
            logger.error(f"Errore durante analisi sistema: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def handle_risk(self) -> None:
        """Handle risk analysis command."""
        self.show_risk_analysis()
    
    def handle_protection(self) -> None:
        """Handle position protection command."""
        self.show_position_protection()
    
    def handle_exchange(self) -> None:
        """Handle exchange status command."""
        self.show_exchange_health()
    
    def handle_health(self) -> None:
        """Handle system health command."""
        self.show_system_health()
    
    def handle_protection_config(self, protection: str) -> None:
        """Handle protection configuration command."""
        self.toggle_protection(protection)
