"""Base classes for DNA System.

Questo modulo contiene le classi base per il sistema DNA:
- Gene: classe base per gli indicatori tecnici
- DNA: gestione strategie di trading
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd

from utils.config import load_config
from utils.logger import get_component_logger
from core.metrics import GeneMetrics, StrategyMetrics, PerformanceMetrics

# Setup logger
logger = get_component_logger('DNA')

class Gene(ABC):
    """Classe base per i geni (indicatori tecnici)."""
    
    def __init__(self, name: str):
        """Inizializza un gene.
        
        Args:
            name: Nome del gene/indicatore
        """
        self.name = name
        self.metrics = GeneMetrics()
        self.signals: List[float] = []
        
        # Carica configurazione
        config = load_config('dna.yaml')
        self.params = config['indicators'].get(name, {})
        
        logger.info(f"Inizializzato gene {name} con parametri: {self.params}")
        
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> np.ndarray:
        """Calcola i valori dell'indicatore.
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Array con i valori calcolati
        """
        pass
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera un segnale di trading [-1, 0, 1].
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Segnale di trading: -1 (sell), 0 (hold), 1 (buy)
        """
        pass
    
    def update_metrics(self, results: Dict[str, float]) -> None:
        """Aggiorna le metriche del gene.
        
        Args:
            results: Dizionario con i risultati delle operazioni
        """
        self.metrics.update(results)
        logger.debug(f"Aggiornate metriche gene {self.name}: {self.metrics.to_dict()}")

    def optimize_params(self, data: pd.DataFrame) -> None:
        """Ottimizza i parametri del gene sui dati forniti."""
        logger.info(f"Avvio ottimizzazione parametri gene {self.name}")
        
        # Calcola segnali con parametri attuali
        signals = np.array([self.generate_signal(data.iloc[:i+1]) 
                          for i in range(len(data))])
                          
        # Aggiorna metriche di auto-tuning
        self.metrics.calculate_auto_tuning_metrics(signals)
        logger.debug(f"Calcolate metriche auto-tuning per {self.name}")
        
        # TODO: Implementare ottimizzazione parametri basata su metriche
        pass

class DNA:
    """Gestisce la struttura delle strategie di trading."""
    
    def __init__(self):
        """Inizializza il DNA system."""
        self.genes: Dict[str, Gene] = {}
        self.config = load_config('dna.yaml')
        self.strategy_metrics = StrategyMetrics()
        self.performance_metrics = PerformanceMetrics()
        self.logger = logger
        
        self.logger.info("Inizializzazione DNA system")
        
    def add_gene(self, gene: Gene) -> None:
        """Aggiunge un gene al DNA.
        
        Args:
            gene: Istanza di Gene da aggiungere
        """
        self.genes[gene.name] = gene
        self.logger.info(f"Aggiunto gene {gene.name} al DNA")
        
    def remove_gene(self, gene_name: str) -> None:
        """Rimuove un gene dal DNA.
        
        Args:
            gene_name: Nome del gene da rimuovere
        """
        if gene_name in self.genes:
            del self.genes[gene_name]
            self.logger.info(f"Rimosso gene {gene_name} dal DNA")
            
    def get_strategy_signal(self, data: pd.DataFrame) -> float:
        """Genera un segnale composito dalla strategia.
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Segnale di trading aggregato: -1 (sell), 0 (hold), 1 (buy)
        """
        if not self.genes:
            self.logger.warning("Nessun gene presente nel DNA")
            return 0
            
        start_time = time.time()
        signals = []
        weights = []
        
        for gene in self.genes.values():
            signal = gene.generate_signal(data)
            fitness = gene.metrics.calculate_fitness()
            
            signals.append(signal)
            weights.append(fitness)
            
        # Normalizza pesi
        weights = np.array(weights) / sum(weights)
        
        # Calcola segnale pesato
        final_signal = np.average(signals, weights=weights)
        
        # Registra latenza
        latency = (time.time() - start_time) * 1000  # ms
        self.performance_metrics.record_signal_latency(latency)
        
        self.logger.debug(f"Generato segnale strategia: {final_signal}")
        return final_signal
        
    def optimize_strategy(self, data: pd.DataFrame) -> None:
        """Ottimizza tutti i geni della strategia.
        
        Args:
            data: DataFrame con i dati OHLCV
        """
        self.logger.info("Avvio ottimizzazione strategia")
        
        start_time = time.time()
        
        # Ottimizza ogni gene
        for gene in self.genes.values():
            gene.optimize_params(data)
            
        # Calcola metriche strategia
        equity_curve = self._calculate_equity_curve(data)
        self.strategy_metrics.calculate_returns_metrics(equity_curve)
        self.strategy_metrics.calculate_risk_metrics(equity_curve)
        
        # Registra latenza
        latency = (time.time() - start_time) * 1000  # ms
        self.performance_metrics.record_execution_latency(latency)
        
        # Aggiorna metriche sistema
        self.performance_metrics.update_system_metrics()
        
    def _calculate_equity_curve(self, data: pd.DataFrame) -> np.ndarray:
        """Calcola la curva equity sui dati storici."""
        equity = np.zeros(len(data))
        position = 0
        
        for i in range(len(data)):
            signal = self.get_strategy_signal(data.iloc[:i+1])
            
            if signal > 0.5 and position <= 0:
                position = 1  # Long
            elif signal < -0.5 and position >= 0:
                position = -1  # Short
                
            returns = data['close'].pct_change().iloc[i]
            equity[i] = equity[i-1] * (1 + position * returns) if i > 0 else 1
            
        return equity
