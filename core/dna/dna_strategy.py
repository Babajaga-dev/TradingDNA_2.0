"""DNA strategy module for signal generation and metrics.

Questo modulo contiene la logica per la generazione dei segnali e il monitoraggio delle metriche.
"""
import time
from typing import Dict, List
import logging
import numpy as np
import pandas as pd
from .dna_base import DNABase

logger = logging.getLogger(__name__)

class DNAStrategy(DNABase):
    """Gestisce la generazione dei segnali e le metriche della strategia."""

    def get_strategy_metrics(self) -> Dict[str, float]:
        """Restituisce le metriche correnti della strategia.
        
        Returns:
            Dict[str, float]: Dizionario con le metriche della strategia
        """
        return {
            'win_rate': getattr(self.strategy_metrics, 'win_rate', 0.0),
            'profit_factor': getattr(self.strategy_metrics, 'profit_factor', 0.0),
            'sharpe_ratio': getattr(self.strategy_metrics, 'sharpe_ratio', 0.0),
            'max_drawdown': getattr(self.strategy_metrics, 'max_drawdown', 0.0)
        }

    def get_performance_metrics(self) -> Dict[str, float]:
        """Restituisce le metriche di performance del sistema.
        
        Returns:
            Dict[str, float]: Dizionario con le metriche di performance
                - cpu_usage: Utilizzo CPU (0-1)
                - memory_usage: Utilizzo memoria (0-1)
                - signal_latency: Latenza segnali (ms)
                - execution_latency: Latenza esecuzione (ms)
                - signals_per_second: Throughput segnali
                - health_score: Score salute sistema (0-1)
        """
        return {
            'cpu_usage': getattr(self.performance_metrics, 'cpu_usage', 0.0),
            'memory_usage': getattr(self.performance_metrics, 'memory_usage', 0.0),
            'signal_latency': getattr(self.performance_metrics, 'signal_latency', 0.0),
            'execution_latency': getattr(self.performance_metrics, 'execution_latency', 0.0),
            'signals_per_second': getattr(self.performance_metrics, 'signals_per_second', 0.0),
            'health_score': getattr(self.performance_metrics, 'health_score', 0.0)
        }

    def get_strategy_signal(self, data: pd.DataFrame) -> float:
        """Genera un segnale composito dalla strategia.
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Segnale di trading aggregato: -1 (sell), 0 (hold), 1 (buy)
            
        Raises:
            ValueError: Se i dati non sono validi
        """
        # Validazione input rigorosa
        if data is None:
            raise ValueError("Dati di input nulli")
        
        if data.empty:
            raise ValueError("DataFrame vuoto")
        
        # Controllo colonne richieste
        required_columns = ['close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        # Solleva eccezione se mancano colonne o se le colonne sono solo 'invalid'
        if missing_columns or (len(data.columns) == 1 and list(data.columns)[0] == 'invalid'):
            logger.error(f"Colonne mancanti o non valide: {data.columns}")
            raise ValueError(f"Colonne mancanti o non valide: {data.columns}")
        
        if not self.genes:
            logger.warning("Nessun gene presente nel DNA")
            return 0.0
            
        start_time = time.time()
        signals = []
        weights = []
        
        for gene in self.genes.values():
            try:
                # Gestione dataset piccoli con parametri minimi
                min_data_points = getattr(gene, 'min_data_points', 10)
                if len(data) < min_data_points:
                    logger.warning(f"Dati insufficienti per gene {gene.name}")
                    continue
                
                signal = gene.generate_signal(data)
                
                # Calcolo fitness più robusto
                try:
                    fitness = gene.metrics.calculate_fitness() if hasattr(gene.metrics, 'calculate_fitness') else 1.0
                except Exception:
                    fitness = 1.0
                
                signals.append(signal)
                weights.append(fitness)
            except Exception as e:
                logger.error(f"Errore nel gene {gene.name}: {str(e)}")
        
        # Gestione caso nessun segnale valido
        if not signals:
            logger.warning("Nessun segnale valido generato")
            return 0.0
        
        # Normalizza pesi con softmax
        weights = np.array(weights)
        weights = np.exp(weights) / np.sum(np.exp(weights))
        
        # Calcola segnale pesato
        final_signal = np.average(signals, weights=weights)
        
        # Registra latenza
        latency = (time.time() - start_time) * 1000  # ms
        self.performance_metrics.record_signal_latency(latency)
        
        logger.debug(f"Generato segnale strategia: {final_signal}")
        return float(final_signal)