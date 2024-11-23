"""Handler base per i comandi del sistema DNA."""
from typing import Optional, Dict, Any
import logging
from pathlib import Path
import pandas as pd
from rich import print as rprint

from cli.utils import print_error, print_success
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
            rprint("\n[cyan]Inizializzazione DNA system...\n")
            
            for gene in genes:
                self.dna.add_gene(gene)
            
            rprint("")
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
            # Creo un oggetto con l'attributo type
            class Args:
                def __init__(self, type_):
                    self.type = type_
            args = Args(gene_type)
            handle_gene_analysis(self.dna, args)
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
        """Handle DNA composition analysis."""
        try:
            from cli.handlers.dna_analysis import handle_composition
            if not self.dna.genes:
                print_error("Nessun gene presente. Esegui 'dna init' prima")
                return
            handle_composition(self.dna)
        except Exception as e:
            logger.error(f"Errore durante analisi composizione: {str(e)}")
            print_error(f"Errore: {str(e)}")
            raise
