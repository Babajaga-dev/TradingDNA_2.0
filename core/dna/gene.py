"""Base class for DNA genes.

Questo modulo contiene la classe base Gene per gli indicatori tecnici.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Union, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from utils.config import load_config
from utils.logger_base import get_component_logger
from core.metrics import GeneMetrics

# Setup logger
logger = get_component_logger('Gene')

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
        self.param_bounds = config['optimization'].get(name, {})
        
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Union[np.ndarray, Tuple[np.ndarray, ...]]:
        """Calcola i valori dell'indicatore.
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Array o tupla di array con i valori calcolati
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

    def get_state(self) -> Dict[str, float]:
        """Restituisce lo stato corrente del gene.
        
        Returns:
            Dict[str, float]: Dizionario con i parametri correnti
        """
        return self.params

    def _calculate_fitness(self, params: np.ndarray, data: pd.DataFrame) -> float:
        """Calcola il fitness score per un set di parametri.
        
        Args:
            params: Array con i parametri da testare
            data: DataFrame con i dati OHLCV
            
        Returns:
            float: Fitness score (negativo per minimizzazione)
        """
        # Aggiorna temporaneamente i parametri
        original_params = self.params.copy()
        param_names = list(self.param_bounds.keys())
        
        for i, name in enumerate(param_names):
            self.params[name] = params[i]
            
        try:
            # Genera segnali con i nuovi parametri
            signals = np.array([self.generate_signal(data.iloc[:i+1]) 
                              for i in range(len(data))])
            
            # Calcola returns
            returns = data['close'].pct_change().values
            strategy_returns = signals[:-1] * returns[1:]
            
            # Calcola metriche
            total_return = np.sum(strategy_returns)
            volatility = np.std(strategy_returns)
            max_drawdown = np.min(np.cumsum(strategy_returns))
            
            # Sharpe ratio come metrica principale
            sharpe = total_return / (volatility + 1e-6)
            
            # Penalizza drawdown eccessivi
            if max_drawdown < -0.2:
                sharpe *= 0.5
                
            # Penalizza overfit
            num_trades = np.sum(np.diff(signals) != 0)
            if num_trades > len(data) * 0.1:
                sharpe *= 0.8
                
            # Ritorna negativo per minimizzazione
            return -sharpe
            
        finally:
            # Ripristina parametri originali
            self.params = original_params

    def optimize(self, data: pd.DataFrame) -> None:
        """Ottimizza i parametri del gene sui dati forniti."""
        if not self.param_bounds:
            return
            
        try:
            # Prepara bounds e parametri iniziali
            param_names = list(self.param_bounds.keys())
            bounds = [self.param_bounds[p] for p in param_names]
            initial_params = [self.params[p] for p in param_names]
            
            # Esegui ottimizzazione
            result = minimize(
                self._calculate_fitness,
                initial_params,
                args=(data,),
                bounds=bounds,
                method='SLSQP'
            )
            
            if result.success:
                # Aggiorna parametri ottimizzati
                for i, name in enumerate(param_names):
                    self.params[name] = result.x[i]
                    
                # Calcola e aggiorna metriche con nuovi parametri
                signals = np.array([self.generate_signal(data.iloc[:i+1]) 
                                  for i in range(len(data))])
                self.metrics.calculate_auto_tuning_metrics(signals)
                
        except Exception as e:
            logger.debug(f"Errore nell'ottimizzazione {self.name}: {str(e)}")
            raise
