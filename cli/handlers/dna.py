"""Handler per i comandi del sistema DNA."""
import time
from pathlib import Path
import pandas as pd
from rich.table import Table
from rich.panel import Panel

from cli.utils import show_progress, console, print_error, print_success
from utils.logger_base import get_component_logger
from core.dna import DNA, RSIGene, MACDGene, BollingerGene, VolumeGene
from core.dna.pattern_recognition import PatternRecognition

# Setup logger
logger = get_component_logger('DNAHandler')

def load_market_data(pair: str = "BTC/USDT", timeframe: str = "1h") -> pd.DataFrame:
    """Carica i dati di mercato dal file parquet.
    
    Args:
        pair: Coppia di trading (default: BTC/USDT)
        timeframe: Timeframe (default: 1h)
        
    Returns:
        DataFrame con i dati OHLCV
        
    Raises:
        FileNotFoundError: Se il file dati non esiste
    """
    data_path = Path(f"data/market/{pair.replace('/', '_')}_{timeframe}_training.parquet")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Dati non trovati per {pair} {timeframe}")
        
    return pd.read_parquet(data_path)

def handle_gene_analysis(dna: DNA, args) -> None:
    """Gestisce l'analisi di un singolo gene."""
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

def handle_optimization(dna: DNA) -> None:
    """Gestisce l'ottimizzazione dei parametri."""
    try:
        data = load_market_data()
        
        with show_progress("Ottimizzazione DNA") as progress:
            task = progress.add_task("Ottimizzazione parametri...", total=100)
            
            train_size = int(len(data) * 0.7)
            train_data = data.iloc[:train_size]
            
            for gene in dna.genes.values():
                gene.optimize_params(train_data)
                progress.update(task, advance=100/len(dna.genes))
        
        table = Table(title="Parametri Ottimizzati")
        table.add_column("Gene", style="cyan")
        table.add_column("Parametri", style="green")
        table.add_column("Fitness", style="yellow")
        
        for name, gene in dna.genes.items():
            table.add_row(
                name,
                str(gene.params),
                f"{gene.metrics.calculate_fitness():.4f}"
            )
        
        console.print("\n")
        console.print(table)
        print_success("Ottimizzazione completata")
        
    except Exception as e:
        print_error(f"Errore ottimizzazione: {str(e)}")

def handle_validation(dna: DNA) -> None:
    """Gestisce la validazione della strategia."""
    try:
        data = load_market_data()
        
        with show_progress("Validazione Strategia") as progress:
            task = progress.add_task("Validazione...", total=100)
            metrics = dna.validate_strategy(data)
            progress.update(task, completed=100)
        
        table = Table(title="Metriche Validazione")
        table.add_column("Metrica", style="cyan")
        table.add_column("Valore", style="green")
        
        for metric, value in metrics.items():
            table.add_row(
                metric.replace('_', ' ').title(),
                f"{value:.4f}"
            )
        
        console.print("\n")
        console.print(table)
        print_success("Validazione completata")
        
    except Exception as e:
        print_error(f"Errore validazione: {str(e)}")

def handle_composition(dna: DNA) -> None:
    """Gestisce la composizione dei segnali."""
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

def handle_dna_command(args) -> None:
    """Gestisce i comandi del sistema DNA."""
    logger.info(f"Esecuzione comando DNA: {args.action}")
    
    try:
        dna = DNA()
        
        if args.action == "init":
            genes = [
                PatternRecognition(),
                RSIGene(),
                MACDGene(),
                BollingerGene(),
                VolumeGene()
            ]
            
            with show_progress("Inizializzazione DNA") as progress:
                task = progress.add_task("Aggiunta geni...", total=len(genes))
                for gene in genes:
                    dna.add_gene(gene)
                    progress.update(task, advance=1)
                    time.sleep(0.1)
                    
            logger.info("DNA inizializzato con tutti i geni")
            print_success("DNA inizializzato con successo")
            
        elif args.action == "gene":
            handle_gene_analysis(dna, args)
            
        elif args.action == "optimize":
            if not dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_optimization(dna)
            
        elif args.action == "validate":
            if not dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_validation(dna)
            
        elif args.action == "compose":
            if not dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_composition(dna)
            
        else:
            print_error(f"Azione {args.action} non valida")
            
    except Exception as e:
        logger.error(f"Errore durante esecuzione comando DNA: {str(e)}")
        print_error(f"Errore: {str(e)}")
