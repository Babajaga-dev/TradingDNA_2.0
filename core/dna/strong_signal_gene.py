"""Gene per la generazione di segnali forti basati sul trend.

Questo modulo implementa il gene StrongSignal che genera segnali
basati sull'analisi del trend dei prezzi.
"""
from typing import Dict, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
from utils.logger_base import get_component_logger
from core.dna.gene import Gene

# Setup logger
logger = get_component_logger('StrongSignalGene')

class StrongSignalGene(Gene):
    """Gene per la generazione di segnali forti basati sul trend."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Inizializza il gene StrongSignal.
        
        Args:
            config: Dizionario con parametri di configurazione
        """
        super().__init__("strong_signal")
        
        # Carica configurazione con valori di default
        if config is None:
            config = {}
            
        self.window_size: int = config.get('window_size', 5)
        self.trend_threshold: float = config.get('trend_threshold', 0.001)
        self.signal_multiplier: float = config.get('signal_multiplier', 100.0)
        self.weight: float = config.get('weight', 1.0)
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Calcola i valori del trend.
        
        Args:
            data: DataFrame con colonna 'close' per i prezzi
            
        Returns:
            Dict[str, np.ndarray]: Dizionario contenente:
                - 'returns': Array dei rendimenti
                - 'trend': Array del trend
                
        Raises:
            ValueError: Se manca la colonna 'close' nel DataFrame
        """
        if 'close' not in data.columns:
            logger.debug("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        close_prices = data['close'].values
        returns = np.zeros_like(close_prices)
        trend = np.zeros_like(close_prices)
        
        # Calcola i rendimenti
        returns[1:] = np.diff(close_prices) / close_prices[:-1]
        
        # Calcola il trend usando una finestra mobile
        for i in range(self.window_size-1, len(close_prices)):
            trend[i] = np.mean(returns[i-self.window_size+1:i+1])
            
        return {
            'returns': returns,
            'trend': trend
        }
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato sul trend.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
            
        Raises:
            ValueError: Se il DataFrame è vuoto o manca la colonna 'close'
        """
        if data.empty:
            raise ValueError("DataFrame vuoto")
            
        if 'close' not in data.columns:
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        try:
            # Verifica dati sufficienti
            if len(data) < self.window_size:
                logger.debug(f"Dati insufficienti ({len(data)} < {self.window_size})")
                return 0
                
            # Calcola trend
            calculations = self.calculate(data)
            current_trend = calculations['trend'][-1]
            
            # Genera segnale basato sul trend
            if abs(current_trend) < self.trend_threshold:
                return 0
            
            elif current_trend > 0:
                signal = min(abs(current_trend * self.signal_multiplier), 1.0)
                return signal * self.weight
                
            else:
                signal = -min(abs(current_trend * self.signal_multiplier), 1.0)
                return signal * self.weight
                
        except Exception as e:
            logger.debug(f"Errore nel calcolo del segnale StrongSignal: {str(e)}")
            raise  # Propaga l'errore invece di restituire 0
