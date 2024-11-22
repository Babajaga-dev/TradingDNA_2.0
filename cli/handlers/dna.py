"""Handler principale per i comandi del sistema DNA."""
from typing import Optional, Dict, Any
import time
import sys
from pathlib import Path
import pandas as pd
from rich.table import Table
from rich.panel import Panel

from cli.utils import show_progress, console, print_error, print_success
from utils.logger_base import get_component_logger
from utils.config import load_config
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

def initialize_dna(dna: DNA) -> None:
    """Inizializza il sistema DNA con tutti i geni.
    
    Args:
        dna: Istanza DNA da inizializzare
        
    Raises:
        Exception: Se si verifica un errore durante l'inizializzazione
    """
    try:
        config = load_config('dna.yaml')
        
        genes = [
            PatternRecognition(config['indicators']['pattern_recognition']),
            RSIGene(config['indicators']['rsi']),
            MACDGene(config['indicators']['macd']),
            BollingerGene(config['indicators']['bollinger']),
            VolumeGene(config['indicators']['volume'])
        ]
        
        with show_progress("Inizializzazione DNA") as progress:
            task = progress.add_task("Aggiunta geni...", total=len(genes))
            for gene in genes:
                dna.add_gene(gene)
                progress.update(task, advance=1)
                time.sleep(0.1)
                
        logger.info("DNA inizializzato con tutti i geni")
        print_success("DNA inizializzato con successo")
        
    except Exception as e:
        logger.error(f"Errore durante inizializzazione DNA: {str(e)}")
        print_error(f"Errore durante inizializzazione: {str(e)}")
        raise

def handle_dna(args: Any) -> None:
    """Gestisce i comandi del sistema DNA.
    
    Args:
        args: Argomenti del comando
        
    Raises:
        ValueError: Se l'azione non è valida
    """
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
            
        else:
            print_error(f"Azione {args.action} non valida")
            raise ValueError(f"Azione {args.action} non valida")
            
    except Exception as e:
        logger.error(f"Errore durante esecuzione comando DNA: {str(e)}")
        print_error(f"Errore: {str(e)}")
        sys.exit(1)
