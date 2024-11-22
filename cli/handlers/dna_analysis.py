"""Funzioni di analisi per il sistema DNA."""
from typing import Dict, Any
import pandas as pd
from rich.table import Table
from rich.panel import Panel

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
        
        if isinstance(values, tuple):
            for i, v in enumerate(values):
                table.add_row(f"Output {i+1}", f"{v[-1]:.4f}")
        else:
            table.add_row("Valore", f"{values[-1]:.4f}")
            
        signal_map = {1: "🟢 BUY", 0: "⚪ HOLD", -1: "🔴 SELL"}
        table.add_row("Segnale", signal_map[signal])
        
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
        
        signal_map = {1: "🟢 BUY", 0: "⚪ HOLD", -1: "🔴 SELL"}
        
        for name in signals:
            table.add_row(
                name,
                signal_map[signals[name]],
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
