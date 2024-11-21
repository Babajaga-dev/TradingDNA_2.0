"""Gene per il calcolo del Moving Average Convergence Divergence.

Questo modulo implementa il gene MACD che calcola e genera segnali
basati sull'indicatore Moving Average Convergence Divergence.
"""
from typing import Dict
import numpy as np
import pandas as pd
from utils.logger import get_component_logger
from core.dna.base import Gene

# Setup logger
logger = get_component_logger('MACDGene')

class MACDGene(Gene):
    """Gene per il calcolo del Moving Average Convergence Divergence."""
    
    def __init__(self) -> None:
        """Inizializza il gene MACD."""
        super().__init__("macd")
        self.fast_period: int = self.params.get('fast_period', 12)
        self.slow_period: int = self.params.get('slow_period', 26)
        self.signal_period: int = self.params.get('signal_period', 9)
        self.signal_threshold: float = self.params.get('signal_threshold', 0.0)
        logger.info(
            f"Inizializzato MACD con periodi {self.fast_period}/"
            f"{self.slow_period}/{self.signal_period}"
        )
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Calcola i valori MACD.
        
        Args:
            data: DataFrame con colonna 'close' per i prezzi
            
        Returns:
            Dict[str, np.ndarray]: Dictionary con:
                - macd: linea MACD principale
                - signal: linea del segnale
                - histogram: istogramma MACD
                
        Raises:
            ValueError: Se manca la colonna 'close' nel DataFrame
        """
        if 'close' not in data.columns:
            logger.error("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        close = data['close'].values
        exp1 = pd.Series(close).ewm(span=self.fast_period, adjust=False).mean()
        exp2 = pd.Series(close).ewm(span=self.slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = pd.Series(macd).ewm(span=self.signal_period, adjust=False).mean()
        hist = macd - signal
        
        logger.debug(
            f"Calcolato MACD, ultimi valori: MACD={macd[-1]:.4f}, "
            f"Signal={signal[-1]:.4f}, Hist={hist[-1]:.4f}"
        )
        
        return {
            'macd': macd.values,
            'signal': signal.values,
            'histogram': hist.values
        }
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato su MACD.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            values = self.calculate(data)
            hist = values['histogram']
            current_hist = hist[-1]
            prev_hist = hist[-2]
            
            if current_hist > self.signal_threshold and current_hist > prev_hist:
                logger.info(
                    f"MACD crossover rialzista (hist: {current_hist:.4f} > "
                    f"{prev_hist:.4f}), signal: 1"
                )
                return 1
                
            elif current_hist < -self.signal_threshold and current_hist < prev_hist:
                logger.info(
                    f"MACD crossover ribassista (hist: {current_hist:.4f} < "
                    f"{prev_hist:.4f}), signal: -1"
                )
                return -1
                
            logger.debug(f"MACD neutrale (hist: {current_hist:.4f}), nessun segnale")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale MACD: {str(e)}")
            return 0
