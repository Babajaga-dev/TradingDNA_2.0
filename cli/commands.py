"""
Comandi CLI per TradingDNA 2.0
"""
import time
import sys
from pathlib import Path
import pandas as pd
from rich.table import Table

from cli.utils import show_progress, console, print_error, print_success
from cli.handlers.log import handle_log
from cli.handlers.download import handle_download
from cli.handlers.config import handle_config
from utils.logger import get_component_logger
from utils.initializer import Initializer, InitializationError
from core.dna import DNA
from core.dna.pattern_recognition import PatternRecognition

# Setup logger
logger = get_component_logger('CLI')

def handle_immune():
    """Gestisce il Sistema Immunitario"""
    with show_progress("Sistema Immunitario") as progress:
        task = progress.add_task("Analisi rischi...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[red]Sistema Immunitario - Non ancora implementato[/]")

def handle_metabolism():
    """Gestisce il Sistema Metabolismo"""
    with show_progress("Sistema Metabolismo") as progress:
        task = progress.add_task("Analisi capitale...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[green]Sistema Metabolismo - Non ancora implementato[/]")

def handle_nervous():
    """Gestisce il Sistema Nervoso"""
    with show_progress("Sistema Nervoso") as progress:
        task = progress.add_task("Analisi dati...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[blue]Sistema Nervoso - Non ancora implementato[/]")

def handle_endocrine():
    """Gestisce il Sistema Endocrino"""
    with show_progress("Sistema Endocrino") as progress:
        task = progress.add_task("Ottimizzazione parametri...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[magenta]Sistema Endocrino - Non ancora implementato[/]")

def handle_reproductive():
    """Gestisce il Sistema Riproduttivo"""
    with show_progress("Sistema Riproduttivo") as progress:
        task = progress.add_task("Evoluzione strategie...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.02)
    console.print("[yellow]Sistema Riproduttivo - Non ancora implementato[/]")

def handle_init(args):
    """Gestisce il comando init"""
    logger.info("Avvio inizializzazione sistema")
    try:
        initializer = Initializer(force=args.force)
        initializer.initialize()  # Chiamata una sola volta
        
        # Progress bar solo se l'inizializzazione ha successo
        with show_progress("Inizializzazione sistema") as progress:
            task = progress.add_task("Setup completato", total=100)
            progress.update(task, advance=100)  # Aggiorna subito al 100%
            
    except InitializationError as e:
        logger.error(f"Errore di inizializzazione: {str(e)}")
        print_error(f"Errore di inizializzazione: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Errore: {str(e)}")
        print_error(f"Errore: {str(e)}")
        sys.exit(1)
        
    logger.info("Inizializzazione completata con successo")
    return True

def handle_dna(args):
    """Gestisce il comando dna"""
    logger.info(f"Esecuzione comando DNA: {args.action}")
    
    try:
        dna = DNA()  # Inizializza il sistema DNA
        
        if args.action == "init":
            # Inizializza DNA con Pattern Recognition
            gene = PatternRecognition()
            dna.add_gene(gene)
            logger.info("Inizializzato DNA con Pattern Recognition")
            print_success("DNA inizializzato con Pattern Recognition")
            
        elif args.action == "analyze":
            # Verifica presenza gene Pattern Recognition
            pattern_gene = next((g for g in dna.genes.values() 
                               if isinstance(g, PatternRecognition)), None)
            
            if not pattern_gene:
                logger.warning("Pattern Recognition non presente")
                print_error("Gene Pattern Recognition non trovato. Esegui 'dna init' prima.")
                return
                
            # Carica dati
            pair = args.pair or "BTC/USDT"
            timeframe = args.timeframe or "1h"
            data_path = Path(f"data/market/{pair.replace('/', '_')}_{timeframe}_training.parquet")
            
            if not data_path.exists():
                logger.error(f"File dati non trovato: {data_path}")
                print_error(f"Dati non trovati per {pair} {timeframe}")
                return
                
            data = pd.read_parquet(data_path)
            logger.info(f"Caricati {len(data)} dati per analisi pattern")
            
            # Analisi pattern
            with show_progress("Analisi Pattern") as progress:
                task = progress.add_task("[cyan]Analisi pattern...", total=len(data))
                pattern_scores = pattern_gene.calculate(data)
                progress.update(task, completed=len(data))
            
            # Mostra risultati
            table = Table(title="Analisi Pattern", show_header=True)
            table.add_column("Metrica", style="cyan")
            table.add_column("Valore", style="green")
            
            table.add_row("Pattern Identificati", str(len(pattern_gene.patterns)))
            table.add_row("Score Medio", f"{pattern_scores.mean():.3f}")
            table.add_row("Score Massimo", f"{pattern_scores.max():.3f}")
            
            console.print("\n")
            console.print(table)
            logger.info(f"Analisi pattern completata: {len(pattern_gene.patterns)} pattern trovati")
            print_success("Analisi pattern completata")
            
        elif args.action == "indicators":
            logger.warning("Indicatori tecnici non ancora implementati")
            print_error("Indicatori tecnici - Funzionalità in sviluppo")
            
        elif args.action == "score":
            if not dna.genes:
                logger.warning("Nessun gene presente per scoring")
                print_error("Aggiungi geni al DNA prima di calcolare gli score")
                return
                
            # Calcola e mostra metriche
            table = Table(title="DNA Scoring", show_header=True)
            table.add_column("Gene", style="cyan")
            table.add_column("Fitness", style="green")
            table.add_column("Win Rate", style="yellow")
            table.add_column("Profit Factor", style="magenta")
            
            for name, gene in dna.genes.items():
                metrics = gene.metrics.to_dict()
                table.add_row(
                    name,
                    f"{metrics['fitness']:.2f}",
                    f"{metrics['win_rate']:.2f}",
                    f"{metrics['profit_factor']:.2f}"
                )
            
            console.print("\n")
            console.print(table)
            logger.info("Scoring DNA completato")
            print_success("Scoring completato")
            
    except Exception as e:
        logger.error(f"Errore durante esecuzione comando DNA: {str(e)}")
        print_error(f"Errore: {str(e)}")
        sys.exit(1)
