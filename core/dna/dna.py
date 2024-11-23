"""DNA class for strategy management.

Questo modulo contiene la classe DNA per la gestione delle strategie di trading.
"""
import logging
from typing import Dict, Optional
import pandas as pd

from .dna_base import DNABase
from .dna_strategy import DNAStrategy
from .dna_optimization import DNAOptimization

logger = logging.getLogger(__name__)

class DNA(DNABase):
    """Gestisce la struttura delle strategie di trading."""
    
    _instance: Optional['DNA'] = None
    
    def __init__(self):
        """Inizializza il DNA system."""
        super().__init__()
        self._strategy = DNAStrategy()
        self._optimization = DNAOptimization()
        logger.info("DNA system inizializzato con tutti i componenti")

    @classmethod
    def get_instance(cls) -> 'DNA':
        """Restituisce l'istanza singleton del DNA.
        
        Returns:
            DNA: Istanza singleton
        """
        if cls._instance is None:
            cls._instance = DNA()
        return cls._instance

    def get_strategy_metrics(self) -> Dict[str, float]:
        """Restituisce le metriche correnti della strategia.
        
        Returns:
            Dict[str, float]: Dizionario con le metriche della strategia
        """
        return self._strategy.get_strategy_metrics()

    def get_performance_metrics(self) -> Dict[str, float]:
        """Restituisce le metriche di performance del sistema.
        
        Returns:
            Dict[str, float]: Dizionario con le metriche di performance
        """
        return self._strategy.get_performance_metrics()

    def get_strategy_signal(self, data: pd.DataFrame) -> float:
        """Genera un segnale composito dalla strategia.
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Segnale di trading aggregato: -1 (sell), 0 (hold), 1 (buy)
            
        Raises:
            ValueError: Se i dati non sono validi
        """
        return self._strategy.get_strategy_signal(data, self.genes)

    def validate_strategy(self, data: pd.DataFrame) -> Dict[str, float]:
        """Valida la strategia su un set di dati.
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Dict[str, float]: Metriche di validazione
            
        Raises:
            ValueError: Se i dati non sono validi
        """
        return self._optimization.validate_strategy(data, self.genes)

    def optimize_strategy(self, data: pd.DataFrame) -> None:
        """Ottimizza tutti i geni della strategia.
        
        Args:
            data: DataFrame con i dati OHLCV
        """
        self._optimization.optimize_strategy(data, self.genes)
