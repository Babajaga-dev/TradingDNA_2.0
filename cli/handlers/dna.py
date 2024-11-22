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

# Setup logger
logger = get_component_logger('DNAHandler')

def load_market_data(pair: str = "BTC/USDT", timeframe: str = "1h") -> pd.DataFrame:
    """Carica i dati di mercato dal file parquet."""
    data_path = Path(f"data/market/{pair.replace('/', '_')}_{timeframe}_training.parquet")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Dati non trovati per {pair} {timeframe}")
        
    return pd.read_parquet(data_path)

def initialize_dna(dna: DNA) -> None:
    """Inizializza il sistema DNA con tutti i geni."""
    try:
        config = load_config('dna.yaml')
        
        # Prepara tutti i geni
        logger.info("Preparazione geni...")
        genes = [
            PatternRecognition(config['indicators']['pattern_recognition']),
            RSIGene(config['indicators']['rsi']),
            MACDGene(config['indicators']['macd']),
            BollingerGene(config['indicators']['bollinger']),
            VolumeGene(config['indicators']['volume'])
        ]
        
        # Aggiungi i geni con progress bar
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
                dna.add_gene(gene)
                progress.advance(task_id)
        
        console.print("")
        logger.info("DNA inizializzato con tutti i geni")
        print_success("DNA inizializzato con successo")
        
    except Exception as e:
        logger.error(f"Errore durante inizializzazione DNA: {str(e)}")
        print_error(f"Errore durante inizializzazione: {str(e)}")
        raise

def handle_indicators(dna: DNA) -> None:
    """Gestisce la visualizzazione degli indicatori tecnici."""
    try:
        if not dna.genes:
            print_error("Nessun gene presente. Esegui 'dna init' prima")
            return
            
        # Carica dati recenti
        data = load_market_data()
        
        # Tabella stati geni
        gene_table = Table(title="Stati Geni", border_style="cyan", show_header=True)
        gene_table.add_column("Gene", style="cyan", width=20, justify="left")
        gene_table.add_column("Stato", style="white", width=10, justify="left")
        gene_table.add_column("Parametri", style="white", justify="left")
        
        for gene in dna.genes.values():
            params = gene.get_state()
            params_str = ", ".join(f"{k}: {v}" for k,v in params.items())
            gene_table.add_row(
                gene.__class__.__name__.replace('Gene', ''),
                "Attivo",
                params_str.strip()
            )
            
        console.print(gene_table)
        console.print("")
        
        # Tabella segnali correnti
        signals_table = Table(title="Segnali Correnti", border_style="cyan", show_header=True)
        signals_table.add_column("Gene", style="cyan", width=20, justify="left")
        signals_table.add_column("Segnale", style="white", width=10, justify="left")
        signals_table.add_column("Forza", style="white", width=10, justify="right")
        
        for gene in dna.genes.values():
            signal = gene.generate_signal(data)
            signal_str = "🟢 BUY" if signal > 0.3 else "🔴 SELL" if signal < -0.3 else "⚪ HOLD"
            signals_table.add_row(
                gene.__class__.__name__.replace('Gene', ''),
                signal_str,
                f"{abs(signal):.2f}"
            )
            
        console.print(signals_table)
        console.print("")
        
        # Tabella metriche performance
        metrics_table = Table(title="Metriche Performance", border_style="cyan", show_header=True)
        metrics_table.add_column("Gene", style="cyan", width=20, justify="left")
        metrics_table.add_column("Win Rate", style="white", width=12, justify="right")
        metrics_table.add_column("Profit Factor", style="white", width=15, justify="right")
        metrics_table.add_column("Fitness", style="white", width=10, justify="right")
        
        for gene in dna.genes.values():
            metrics = gene.metrics.to_dict()
            metrics_table.add_row(
                gene.__class__.__name__.replace('Gene', ''),
                f"{metrics.get('win_rate', 0.0)*100:.1f}%",
                f"{metrics.get('profit_factor', 0.0):.2f}",
                f"{metrics.get('fitness', 0.0):.2f}"
            )
            
        console.print(metrics_table)
        console.print("")
        
        # Panel performance strategia
        strategy_metrics = dna.get_strategy_metrics()
        signal = dna.get_strategy_signal(data)
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

def handle_score(dna: DNA) -> None:
    """Gestisce la visualizzazione del punteggio complessivo del sistema DNA."""
    try:
        if not dna.genes:
            print_error("Nessun gene presente. Esegui 'dna init' prima")
            return

        # Carica dati recenti per calcolo metriche
        data = load_market_data()
        
        # Calcola metriche per ogni categoria
        gene_metrics = {}
        for gene in dna.genes.values():
            gene_metrics[gene.__class__.__name__.replace('Gene', '')] = gene.metrics.to_dict()
            
        strategy_metrics = dna.get_strategy_metrics()
        performance_metrics = dna.get_performance_metrics()
        
        # Calcola punteggi medi per categoria
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
        
        # Calcola health score complessivo
        health_score = (gene_score * 0.4 + strategy_score * 0.4 + system_score * 0.2)
        
        # Crea tabella principale
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
        
        # Crea panel con la tabella
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

def handle_dna(args: Any) -> None:
    """Gestisce i comandi del sistema DNA."""
    logger.info(f"Esecuzione comando DNA: {args.action}")
    
    try:
        dna = DNA()
        
        if args.action == "init":
            initialize_dna(dna)
            
        elif args.action == "gene":
            from cli.handlers.dna_analysis import handle_gene_analysis
            handle_gene_analysis(dna, args)
            
        elif args.action == "optimize":
            from cli.handlers.dna_optimization import handle_optimization
            if not dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_optimization(dna)
            
        elif args.action == "validate":
            from cli.handlers.dna_optimization import handle_validation
            if not dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_validation(dna)
            
        elif args.action == "compose":
            from cli.handlers.dna_analysis import handle_composition
            if not dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_composition(dna)
            
        elif args.action == "analyze":
            from cli.handlers.dna_analysis import handle_analysis
            if not dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_analysis(dna)
            
        elif args.action == "indicators":
            handle_indicators(dna)
            
        elif args.action == "score":
            handle_score(dna)
            
        else:
            print_error(f"Azione {args.action} non valida")
            raise ValueError(f"Azione {args.action} non valida")
            
    except Exception as e:
        logger.error(f"Errore durante esecuzione comando DNA: {str(e)}")
        print_error(f"Errore: {str(e)}")
        sys.exit(1)
