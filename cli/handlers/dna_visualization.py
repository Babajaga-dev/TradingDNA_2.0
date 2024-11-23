"""Handler per la visualizzazione del sistema DNA."""
from typing import Dict, List
import pandas as pd
from pathlib import Path
import logging
from rich.table import Table
from rich.panel import Panel
from rich.console import Group
from rich import print as rprint

from cli.utils import show_progress, console, print_error, print_success
from utils.logger_base import get_component_logger
from core.dna import DNA

logger = get_component_logger('DNAVisualization')

class DNAVisualizationHandler:
    """Handler class for DNA visualization operations."""
    
    def __init__(self, dna: DNA):
        """Initialize the visualization handler."""
        self.dna = dna
        
    def handle_pattern_analysis(self, data: pd.DataFrame) -> None:
        """Handle pattern recognition analysis visualization."""
        try:
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
                
            # Trova il gene PatternRecognition
            pattern_gene = None
            for gene in self.dna.genes.values():
                if gene.__class__.__name__ == 'PatternRecognition':
                    pattern_gene = gene
                    break
                    
            if not pattern_gene:
                print_error("Gene PatternRecognition non trovato")
                return
                
            # Calcola i pattern
            with show_progress("Analisi Pattern") as progress:
                task = progress.add_task("Elaborazione...", total=100)
                scores = pattern_gene.calculate(data)
                progress.update(task, completed=100)
                
            # Crea tabella dei pattern trovati
            patterns_table = Table(title="Pattern Identificati", border_style="cyan")
            patterns_table.add_column("Inizio", style="cyan")
            patterns_table.add_column("Fine", style="cyan")
            patterns_table.add_column("Confidenza", style="white")
            patterns_table.add_column("Correlazione", style="white")
            patterns_table.add_column("Qualità", style="white")
            
            for pattern in pattern_gene.patterns[-10:]:  # Mostra ultimi 10 pattern
                start_date = data.index[pattern.start_idx].strftime('%Y-%m-%d %H:%M')
                end_date = data.index[pattern.end_idx].strftime('%Y-%m-%d %H:%M')
                
                patterns_table.add_row(
                    start_date,
                    end_date,
                    f"{pattern.confidence:.2f}",
                    f"{pattern.correlation:.2f}",
                    f"{pattern.quality_score:.2f}"
                )
                
            console.print("\n")
            console.print(patterns_table)
            
            # Crea pannello statistiche
            stats_table = Table(show_header=False, show_edge=False, box=None, padding=0)
            stats_table.add_column(justify="left")
            
            total_patterns = len(pattern_gene.patterns)
            avg_confidence = sum(p.confidence for p in pattern_gene.patterns) / total_patterns if total_patterns > 0 else 0
            avg_correlation = sum(abs(p.correlation) for p in pattern_gene.patterns) / total_patterns if total_patterns > 0 else 0
            avg_quality = sum(p.quality_score for p in pattern_gene.patterns) / total_patterns if total_patterns > 0 else 0
            
            stats_table.add_row(f"Pattern Totali: {total_patterns}")
            stats_table.add_row(f"Confidenza Media: {avg_confidence:.2f}")
            stats_table.add_row(f"Correlazione Media: {avg_correlation:.2f}")
            stats_table.add_row(f"Qualità Media: {avg_quality:.2f}")
            
            stats_panel = Panel(
                stats_table,
                title="Statistiche Pattern",
                border_style="cyan",
                padding=(1, 2)
            )
            
            console.print("\n")
            console.print(stats_panel)
            
            # Genera segnale corrente
            signal = pattern_gene.generate_signal(data)
            signal_str = "🟢 BUY" if signal > 0.3 else "🔴 SELL" if signal < -0.3 else "⚪ HOLD"
            
            signal_panel = Panel(
                f"Segnale: {signal_str} ({signal:.2f})",
                title="Segnale Pattern",
                border_style="cyan",
                padding=(1, 2)
            )
            
            console.print("\n")
            console.print(signal_panel)
            
            logger.info("Visualizzazione pattern completata")
            print_success("Analisi pattern completata")
            
        except Exception as e:
            logger.error(f"Errore durante analisi pattern: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
            
    def handle_indicators(self, data: pd.DataFrame) -> None:
        """Handle technical indicators visualization."""
        try:
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
                
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
            
    def handle_scoring(self, data: pd.DataFrame) -> None:
        """Handle DNA scoring visualization."""
        try:
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return

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
            
    def handle_backtest(self, data: pd.DataFrame) -> None:
        """Handle DNA backtest."""
        try:
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            
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
