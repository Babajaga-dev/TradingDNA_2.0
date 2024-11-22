"""Funzioni di analisi per il sistema DNA."""
from typing import Dict, Any
import pandas as pd
from rich.table import Table
from rich.panel import Panel
from rich.console import Group

from cli.utils import show_progress, console, print_error, print_success
from utils.logger_base import get_component_logger
from core.dna import DNA, RSIGene, MACDGene, BollingerGene, VolumeGene
from .dna import load_market_data

# Setup logger
logger = get_component_logger('DNAAnalysis')

def handle_gene_analysis(dna: DNA, args: Any) -> None:
    """Gestisce l'analisi di un singolo gene.
    
    Args:
        dna: Istanza del DNA
        args: Argomenti del comando
        
    Raises:
        ValueError: Se il tipo di gene non è valido
    """
    gene_map = {
        'rsi': RSIGene(),
        'macd': MACDGene(),
        'bollinger': BollingerGene(),
        'volume': VolumeGene()
    }
    
    if args.type not in gene_map:
        print_error(f"Gene {args.type} non valido")
        return
        
    gene = gene_map[args.type]
    
    try:
        data = load_market_data()
        
        with show_progress(f"Analisi {args.type.upper()}") as progress:
            task = progress.add_task("Calcolo...", total=100)
            
            values = gene.calculate(data)
            signal = gene.generate_signal(data)
            
            progress.update(task, completed=100)
        
        table = Table(title=f"Analisi {args.type.upper()}")
        table.add_column("Metrica", style="cyan")
        table.add_column("Valore", style="green")
        
        if isinstance(values, dict):
            for key, value in values.items():
                table.add_row(key, f"{value[-1]:.4f}")
        elif isinstance(values, tuple):
            for i, v in enumerate(values):
                table.add_row(f"Output {i+1}", f"{v[-1]:.4f}")
        else:
            table.add_row("Valore", f"{values[-1]:.4f}")
            
        # Gestione segnali pesati
        if signal >= 0.3:
            signal_str = "🟢 BUY"
        elif signal <= -0.3:
            signal_str = "🔴 SELL"
        else:
            signal_str = "⚪ HOLD"
            
        table.add_row("Segnale", f"{signal_str} ({signal:.2f})")
        
        console.print("\n")
        console.print(table)
        
    except Exception as e:
        print_error(f"Errore analisi {args.type}: {str(e)}")
        raise

def handle_composition(dna: DNA) -> None:
    """Gestisce la composizione dei segnali.
    
    Args:
        dna: Istanza del DNA
        
    Raises:
        ValueError: Se si verifica un errore nella composizione
    """
    try:
        data = load_market_data()
        
        with show_progress("Composizione Segnali") as progress:
            task = progress.add_task("Analisi...", total=100)
            
            signals = {}
            weights = {}
            
            for name, gene in dna.genes.items():
                signals[name] = gene.generate_signal(data)
                weights[name] = gene.metrics.calculate_fitness()
                progress.update(task, advance=100/len(dna.genes))
            
            final_signal = dna.get_strategy_signal(data)
        
        table = Table(title="Composizione Segnali")
        table.add_column("Gene", style="cyan")
        table.add_column("Segnale", style="yellow")
        table.add_column("Peso", style="green")
        
        # Gestione segnali pesati
        def get_signal_str(signal):
            if signal >= 0.3:
                return "🟢 BUY"
            elif signal <= -0.3:
                return "🔴 SELL"
            return "⚪ HOLD"
        
        for name in signals:
            table.add_row(
                name,
                f"{get_signal_str(signals[name])} ({signals[name]:.2f})",
                f"{weights[name]:.4f}"
            )
        
        console.print("\n")
        console.print(table)
        
        signal_str = "BUY" if final_signal > 0.5 else "SELL" if final_signal < -0.5 else "HOLD"
        color = "green" if final_signal > 0.5 else "red" if final_signal < -0.5 else "yellow"
        
        console.print(Panel(
            f"[{color}]Segnale Finale: {signal_str} ({final_signal:.4f})[/]",
            title="Strategia DNA",
            border_style=color
        ))
        
        print_success("Composizione completata")
        
    except Exception as e:
        print_error(f"Errore composizione: {str(e)}")
        raise

def handle_analysis(dna: DNA) -> None:
    """Gestisce l'analisi completa del sistema DNA.
    
    Args:
        dna: Istanza del DNA
        
    Raises:
        ValueError: Se si verifica un errore nell'analisi
    """
    try:
        data = load_market_data()
        
        with show_progress("Analisi Sistema DNA") as progress:
            task = progress.add_task("Analisi...", total=100)
            
            # Raccolta dati
            gene_signals = {}
            gene_metrics = {}
            gene_states = {}
            
            for name, gene in dna.genes.items():
                gene_signals[name] = gene.generate_signal(data)
                gene_metrics[name] = gene.metrics.to_dict()  # Modificato da get_metrics() a to_dict()
                gene_states[name] = gene.get_state()
                progress.update(task, advance=50/len(dna.genes))
                
            strategy_signal = dna.get_strategy_signal(data)
            strategy_metrics = dna.get_strategy_metrics()
            progress.update(task, completed=100)
            
        # Tabella stati geni
        states_table = Table(title="Stati Geni")
        states_table.add_column("Gene", style="cyan")
        states_table.add_column("Stato", style="yellow")
        states_table.add_column("Parametri", style="green")
        
        for name, state in gene_states.items():
            params = ", ".join(f"{k}: {v:.2f}" for k, v in state.items())
            states_table.add_row(name, "✓ Attivo", params)
            
        # Tabella segnali
        signals_table = Table(title="Segnali Correnti")
        signals_table.add_column("Gene", style="cyan")
        signals_table.add_column("Segnale", style="yellow")
        signals_table.add_column("Forza", style="green")
        
        def get_signal_str(signal):
            if signal >= 0.3:
                return "🟢 BUY"
            elif signal <= -0.3:
                return "🔴 SELL"
            return "⚪ HOLD"
            
        for name, signal in gene_signals.items():
            signals_table.add_row(
                name,
                get_signal_str(signal),
                f"{abs(signal):.2f}"
            )
            
        # Tabella metriche
        metrics_table = Table(title="Metriche Performance")
        metrics_table.add_column("Gene", style="cyan")
        metrics_table.add_column("Win Rate", style="green")
        metrics_table.add_column("Profit Factor", style="green")
        metrics_table.add_column("Fitness", style="green")
        
        for name, metrics in gene_metrics.items():
            metrics_table.add_row(
                name,
                f"{metrics['win_rate']:.2%}",
                f"{metrics['profit_factor']:.2f}",
                f"{metrics['fitness']:.2f}"
            )
            
        # Pannello strategia
        signal_str = "BUY" if strategy_signal > 0.5 else "SELL" if strategy_signal < -0.5 else "HOLD"
        color = "green" if strategy_signal > 0.5 else "red" if strategy_signal < -0.5 else "yellow"
        
        strategy_panel = Panel(
            Group(
                f"[{color}]Segnale Strategia: {signal_str} ({strategy_signal:.4f})[/]",
                "",
                f"Win Rate: {strategy_metrics['win_rate']:.2%}",
                f"Profit Factor: {strategy_metrics['profit_factor']:.2f}",
                f"Sharpe Ratio: {strategy_metrics['sharpe_ratio']:.2f}",
                f"Max Drawdown: {strategy_metrics['max_drawdown']:.2%}"
            ),
            title="Performance Strategia",
            border_style=color
        )
        
        # Output
        console.print("\n")
        console.print(states_table)
        console.print("\n")
        console.print(signals_table)
        console.print("\n")
        console.print(metrics_table)
        console.print("\n")
        console.print(strategy_panel)
        
        print_success("Analisi completata")
        
    except Exception as e:
        print_error(f"Errore durante analisi: {str(e)}")
        raise
