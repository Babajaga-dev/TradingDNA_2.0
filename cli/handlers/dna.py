"""Handler principale per i comandi del sistema DNA."""
from typing import Optional, Dict, Any
import time
import sys
import logging
from pathlib import Path
import pandas as pd
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich import print as rprint

from cli.utils import show_progress, console, print_error, print_success, create_progress
from utils.logger_base import get_component_logger
from utils.config import load_config
from core.dna import DNA, RSIGene, MACDGene, BollingerGene, VolumeGene
from core.dna.pattern_recognition import PatternRecognition

logger = get_component_logger('DNAHandler')

# Funzione wrapper per accesso ai dati di mercato
def load_market_data(pair: str = "BTC/USDT", timeframe: str = "1h") -> pd.DataFrame:
    """Load market data from parquet file."""
    handler = DNAHandler()
    return handler._load_market_data(pair, timeframe)

class DNAHandler:
    """Handler class for DNA System operations."""
    
    def __init__(self):
        """Initialize the DNA handler."""
        self.dna = DNA()
    
    def _load_market_data(self, pair: str = "BTC/USDT", timeframe: str = "1h") -> pd.DataFrame:
        """Load market data from parquet file."""
        data_path = Path(f"data/market/{pair.replace('/', '_')}_{timeframe}_training.parquet")
        
        if not data_path.exists():
            raise FileNotFoundError(f"Dati non trovati per {pair} {timeframe}")
            
        return pd.read_parquet(data_path)
    
    def handle_init(self) -> None:
        """Handle DNA initialization."""
        try:
            config = load_config('dna.yaml')
            
            # Prepare genes
            logger.info("Preparazione geni...")
            genes = [
                PatternRecognition(config['indicators']['pattern_recognition']),
                RSIGene(config['indicators']['rsi']),
                MACDGene(config['indicators']['macd']),
                BollingerGene(config['indicators']['bollinger']),
                VolumeGene(config['indicators']['volume'])
            ]
            
            # Add genes with progress bar
            console.print("\n[cyan]Inizializzazione DNA system...\n")
            
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[cyan]Aggiunta geni..."),
                BarColumn(bar_width=40, style="cyan", complete_style="cyan"),
                TextColumn("[cyan]{task.percentage:>3.0f}%"),
                console=console,
                expand=False,
                transient=True
            )
            
            task_id = progress.add_task("", total=len(genes))
            
            with Live(progress, refresh_per_second=4):
                for gene in genes:
                    self.dna.add_gene(gene)
                    progress.advance(task_id)
            
            console.print("")
            logger.info("DNA inizializzato con tutti i geni")
            print_success("DNA inizializzato con successo")
            
        except Exception as e:
            logger.error(f"Errore durante inizializzazione DNA: {str(e)}")
            print_error(f"Errore durante inizializzazione: {str(e)}")
            raise
    
    def handle_gene(self, gene_type: str) -> None:
        """Handle gene analysis."""
        try:
            from cli.handlers.dna_analysis import handle_gene_analysis
            handle_gene_analysis(self.dna, gene_type)
        except Exception as e:
            logger.error(f"Errore durante analisi gene: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def handle_optimization(self) -> None:
        """Handle DNA optimization."""
        try:
            from cli.handlers.dna_optimization import handle_optimization
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_optimization(self.dna)
        except Exception as e:
            logger.error(f"Errore durante ottimizzazione: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def handle_validation(self) -> None:
        """Handle DNA validation."""
        try:
            from cli.handlers.dna_optimization import handle_validation
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_validation(self.dna)
        except Exception as e:
            logger.error(f"Errore durante validazione: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def handle_composition(self) -> None:
        """Handle DNA composition."""
        try:
            from cli.handlers.dna_analysis import handle_composition
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_composition(self.dna)
        except Exception as e:
            logger.error(f"Errore durante composizione: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def handle_pattern_analysis(self) -> None:
        """Handle pattern analysis."""
        try:
            from cli.handlers.dna_analysis import handle_analysis
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_analysis(self.dna)
        except Exception as e:
            logger.error(f"Errore durante analisi pattern: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def handle_indicators(self) -> None:
        """Handle technical indicators visualization."""
        try:
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
                
            # Load recent data
            data = self._load_market_data()
            
            # Gene states table
            gene_table = Table(title="Stati Geni", border_style="cyan", show_header=True)
            gene_table.add_column("Gene", style="cyan", width=20, justify="left")
            gene_table.add_column("Stato", style="white", width=10, justify="left")
            gene_table.add_column("Parametri", style="white", justify="left")
            
            for gene in self.dna.genes.values():
                params = gene.get_state()
                params_str = ", ".join(f"{k}: {v}" for k,v in params.items())
                gene_table.add_row(
                    gene.__class__.__name__.replace('Gene', ''),
                    "Attivo",
                    params_str.strip()
                )
                
            console.print(gene_table)
            console.print("")
            
            # Current signals table
            signals_table = Table(title="Segnali Correnti", border_style="cyan", show_header=True)
            signals_table.add_column("Gene", style="cyan", width=20, justify="left")
            signals_table.add_column("Segnale", style="white", width=10, justify="left")
            signals_table.add_column("Forza", style="white", width=10, justify="right")
            
            for gene in self.dna.genes.values():
                signal = gene.generate_signal(data)
                signal_str = "🟢 BUY" if signal > 0.3 else "🔴 SELL" if signal < -0.3 else "⚪ HOLD"
                signals_table.add_row(
                    gene.__class__.__name__.replace('Gene', ''),
                    signal_str,
                    f"{abs(signal):.2f}"
                )
                
            console.print(signals_table)
            console.print("")
            
            # Performance metrics table
            metrics_table = Table(title="Metriche Performance", border_style="cyan", show_header=True)
            metrics_table.add_column("Gene", style="cyan", width=20, justify="left")
            metrics_table.add_column("Win Rate", style="white", width=12, justify="right")
            metrics_table.add_column("Profit Factor", style="white", width=15, justify="right")
            metrics_table.add_column("Fitness", style="white", width=10, justify="right")
            
            for gene in self.dna.genes.values():
                metrics = gene.metrics.to_dict()
                metrics_table.add_row(
                    gene.__class__.__name__.replace('Gene', ''),
                    f"{metrics.get('win_rate', 0.0)*100:.1f}%",
                    f"{metrics.get('profit_factor', 0.0):.2f}",
                    f"{metrics.get('fitness', 0.0):.2f}"
                )
                
            console.print(metrics_table)
            console.print("")
            
            # Strategy performance panel
            strategy_metrics = self.dna.get_strategy_metrics()
            signal = self.dna.get_strategy_signal(data)
            signal_type = "BUY" if signal > 0.3 else "SELL" if signal < -0.3 else "HOLD"
            
            strategy_table = Table(show_header=False, show_edge=False, box=None, padding=0)
            strategy_table.add_column(justify="left")
            strategy_table.add_row(f"Segnale: {signal_type} ({abs(signal):.4f})")
            strategy_table.add_row("")
            strategy_table.add_row(f"Win Rate: {strategy_metrics['win_rate']*100:.1f}%")
            strategy_table.add_row(f"Profit Factor: {strategy_metrics.get('profit_factor', 0.0):.2f}")
            strategy_table.add_row(f"Sharpe Ratio: {strategy_metrics.get('sharpe_ratio', 0.0):.2f}")
            strategy_table.add_row(f"Max Drawdown: {strategy_metrics.get('max_drawdown', 0.0)*100:.1f}%")
            
            strategy_panel = Panel(
                strategy_table,
                title="Performance Strategia",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(strategy_panel)
            
            logger.info("Visualizzazione indicatori completata")
            
        except Exception as e:
            logger.error(f"Errore durante analisi indicatori: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
    
    def handle_scoring(self) -> None:
        """Handle DNA scoring visualization."""
        try:
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return

            # Load recent data for metrics calculation
            data = self._load_market_data()
            
            # Calculate metrics for each category
            gene_metrics = {}
            for gene in self.dna.genes.values():
                gene_metrics[gene.__class__.__name__.replace('Gene', '')] = gene.metrics.to_dict()
                
            strategy_metrics = self.dna.get_strategy_metrics()
            performance_metrics = self.dna.get_performance_metrics()
            
            # Calculate average scores by category
            gene_score = sum(m.get('fitness', 0.0) for m in gene_metrics.values()) / len(gene_metrics)
            
            strategy_score = (
                strategy_metrics.get('win_rate', 0.0) * 0.3 +
                min(strategy_metrics.get('profit_factor', 0.0) / 3, 1.0) * 0.3 +
                min(strategy_metrics.get('sharpe_ratio', 0.0) / 2, 1.0) * 0.2 +
                (1 - min(abs(strategy_metrics.get('max_drawdown', 0.0)), 1.0)) * 0.2
            )
            
            system_score = (
                (1 - min(performance_metrics.get('signal_latency', 0.0) / 1000, 1.0)) * 0.4 +
                min(performance_metrics.get('signals_per_second', 0.0) / 100, 1.0) * 0.3 +
                (1 - min(performance_metrics.get('cpu_usage', 0.0), 1.0)) * 0.15 +
                (1 - min(performance_metrics.get('memory_usage', 0.0), 1.0)) * 0.15
            )
            
            # Calculate overall health score
            health_score = (gene_score * 0.4 + strategy_score * 0.4 + system_score * 0.2)
            
            # Create main table
            main_table = Table(show_header=False, show_edge=False, box=None, padding=0)
            main_table.add_column(justify="left")
            main_table.add_row(f"[cyan]DNA Health Score: {health_score:.2f}[/cyan]")
            main_table.add_row("")
            
            # Gene Performance
            main_table.add_row("[cyan]├── Gene Performance[/cyan]")
            for gene_name, metrics in gene_metrics.items():
                main_table.add_row(f"│   ├── {gene_name}: {metrics.get('fitness', 0.0):.2f}")
            main_table.add_row(f"│   └── Score: {gene_score:.2f}")
            main_table.add_row("")
            
            # Strategy Performance
            main_table.add_row("[cyan]├── Strategy Performance[/cyan]")
            main_table.add_row(f"│   ├── Win Rate: {strategy_metrics.get('win_rate', 0.0)*100:.1f}%")
            main_table.add_row(f"│   ├── Profit Factor: {strategy_metrics.get('profit_factor', 0.0):.2f}")
            main_table.add_row(f"│   ├── Sharpe Ratio: {strategy_metrics.get('sharpe_ratio', 0.0):.2f}")
            main_table.add_row(f"│   ├── Max Drawdown: {strategy_metrics.get('max_drawdown', 0.0)*100:.1f}%")
            main_table.add_row(f"│   └── Score: {strategy_score:.2f}")
            main_table.add_row("")
            
            # System Performance
            main_table.add_row("[cyan]└── System Performance[/cyan]")
            main_table.add_row(f"    ├── Latency: {performance_metrics.get('signal_latency', 0.0):.2f}ms")
            main_table.add_row(f"    ├── Throughput: {performance_metrics.get('signals_per_second', 0.0):.1f} sig/s")
            main_table.add_row(f"    ├── CPU Usage: {performance_metrics.get('cpu_usage', 0.0):.1f}%")
            main_table.add_row(f"    ├── Memory Usage: {performance_metrics.get('memory_usage', 0.0):.1f}%")
            main_table.add_row(f"    └── Score: {system_score:.2f}")
            
            # Create panel with table
            score_panel = Panel(
                main_table,
                title="DNA System Score",
                border_style="cyan",
                padding=(1, 2)
            )
            
            console.print("\n")
            console.print(score_panel)
            console.print("\n")
            
            logger.info("Visualizzazione score completata")
            
        except Exception as e:
            logger.error(f"Errore durante calcolo score: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise

    def handle_backtest(self) -> None:
        """Handle DNA backtest."""
        try:
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return

            # Load historical data
            data = self._load_market_data()
            
            console.print("\n[cyan]Avvio backtest DNA...[/cyan]\n")
            
            with show_progress("Backtest in corso") as progress:
                task = progress.add_task("Analisi...", total=100)
                
                # Simulate trading on historical data
                signals = []
                returns = []
                trades = []
                
                for i in range(len(data)-1):
                    current_data = data.iloc[:i+1]
                    signal = self.dna.get_strategy_signal(current_data)
                    price_change = (data.iloc[i+1]['close'] - data.iloc[i]['close']) / data.iloc[i]['close']
                    
                    signals.append(signal)
                    returns.append(price_change if signal > 0.3 else -price_change if signal < -0.3 else 0)
                    
                    if abs(signal) > 0.3:
                        trades.append({
                            'timestamp': data.index[i],
                            'type': 'BUY' if signal > 0.3 else 'SELL',
                            'price': data.iloc[i]['close'],
                            'signal': signal
                        })
                    
                    progress.update(task, advance=100/len(data))
            
            # Calculate performance metrics
            total_return = sum(returns)
            win_trades = sum(1 for r in returns if r > 0)
            total_trades = sum(1 for r in returns if r != 0)
            win_rate = win_trades / total_trades if total_trades > 0 else 0
            
            # Create results table
            results_table = Table(title="Risultati Backtest", border_style="cyan")
            results_table.add_column("Metrica", style="cyan")
            results_table.add_column("Valore", style="white")
            
            results_table.add_row("Periodo", f"{data.index[0].strftime('%Y-%m-%d')} - {data.index[-1].strftime('%Y-%m-%d')}")
            results_table.add_row("Rendimento Totale", f"{total_return*100:.2f}%")
            results_table.add_row("Numero Trade", str(total_trades))
            results_table.add_row("Win Rate", f"{win_rate*100:.1f}%")
            
            console.print(results_table)
            console.print("")
            
            # Create trades table
            if trades:
                trades_table = Table(title="Ultimi Trade", border_style="cyan")
                trades_table.add_column("Data", style="cyan")
                trades_table.add_column("Tipo", style="white")
                trades_table.add_column("Prezzo", style="white")
                trades_table.add_column("Segnale", style="white")
                
                for trade in trades[-5:]:  # Show last 5 trades
                    trades_table.add_row(
                        trade['timestamp'].strftime('%Y-%m-%d %H:%M'),
                        "🟢 BUY" if trade['type'] == 'BUY' else "🔴 SELL",
                        f"{trade['price']:.2f}",
                        f"{abs(trade['signal']):.2f}"
                    )
                
                console.print(trades_table)
            
            logger.info("Backtest completato")
            print_success("Backtest completato con successo")
            
        except Exception as e:
            logger.error(f"Errore durante backtest: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
            
    def handle_config(self) -> None:
        """Handle DNA configuration."""
        try:
            # Load current configuration
            config = load_config('dna.yaml')
            
            # Create configuration table
            config_table = Table(title="Configurazione DNA", border_style="cyan")
            config_table.add_column("Parametro", style="cyan")
            config_table.add_column("Valore", style="white")
            config_table.add_column("Descrizione", style="white")
            
            # Add gene configurations
            for gene_name, params in config['indicators'].items():
                config_table.add_row(
                    f"[cyan]{gene_name.upper()}[/]",
                    "",
                    "Parametri indicatore"
                )
                for param_name, value in params.items():
                    config_table.add_row(
                        f"  {param_name}",
                        str(value),
                        self._get_param_description(gene_name, param_name)
                    )
                config_table.add_row("", "", "")
            
            console.print("\n")
            console.print(config_table)
            console.print("\n")
            
            # Ask if user wants to modify configuration
            choice = console.input("\nModificare la configurazione? [cyan][s/N][/]: ").lower()
            
            if choice == 's':
                self._modify_config(config)
            
            logger.info("Configurazione completata")
            
        except Exception as e:
            logger.error(f"Errore durante configurazione: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
            
    def _get_param_description(self, gene_name: str, param_name: str) -> str:
        """Get parameter description."""
        descriptions = {
            'rsi': {
                'period': 'Periodo per il calcolo RSI',
                'overbought': 'Livello di ipercomprato',
                'oversold': 'Livello di ipervenduto'
            },
            'macd': {
                'fast_period': 'Periodo media mobile veloce',
                'slow_period': 'Periodo media mobile lenta',
                'signal_period': 'Periodo linea del segnale'
            },
            'bollinger': {
                'period': 'Periodo per le bande',
                'std_dev': 'Deviazioni standard'
            },
            'volume': {
                'period': 'Periodo per la media mobile',
                'threshold': 'Soglia variazione volume'
            },
            'pattern_recognition': {
                'min_pattern_length': 'Lunghezza minima pattern',
                'max_pattern_length': 'Lunghezza massima pattern',
                'similarity_threshold': 'Soglia similarità'
            }
        }
        
        return descriptions.get(gene_name, {}).get(param_name, "")
        
    def _modify_config(self, config: Dict) -> None:
        """Modify DNA configuration."""
        modified = False
        
        for gene_name, params in config['indicators'].items():
            console.print(f"\n[cyan]Modifica parametri {gene_name.upper()}[/]")
            
            for param_name, value in params.items():
                new_value = console.input(
                    f"{param_name} [{value}]: "
                ).strip()
                
                if new_value:
                    try:
                        # Convert to appropriate type
                        if isinstance(value, int):
                            params[param_name] = int(new_value)
                        elif isinstance(value, float):
                            params[param_name] = float(new_value)
                        else:
                            params[param_name] = new_value
                        modified = True
                    except ValueError:
                        print_error(f"Valore non valido per {param_name}")
                        continue
        
        if modified:
            # Save configuration
            config_path = Path("config/dna.yaml")
            with open(config_path, 'w') as f:
                import yaml
                yaml.dump(config, f, default_flow_style=False)
            print_success("Configurazione salvata con successo")
            
            # Reinitialize DNA with new configuration
            self.handle_init()