"""Gene per il calcolo del MACD (Moving Average Convergence Divergence).

Questo modulo implementa il gene MACD che calcola e genera segnali
basati sull'indicatore MACD.
"""
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from utils.logger_base import get_component_logger
from core.dna.gene import Gene

# Setup logger
logger = get_component_logger('MACDGene')

class MACDGene(Gene):
    """Gene per il calcolo del MACD."""
    
    def __init__(self) -> None:
        """Inizializza il gene MACD."""
        super().__init__("macd")
        self.fast_period: int = self.params.get('fast_period', 12)
        self.slow_period: int = self.params.get('slow_period', 26)
        self.signal_period: int = self.params.get('signal_period', 9)
        self.signal_threshold: float = self.params.get('signal_threshold', 0.6)
        logger.info(f"Inizializzato MACD con periodi {self.fast_period}/{self.slow_period}/{self.signal_period}")
        
    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calcola l'EMA (Exponential Moving Average).
        
        Args:
            data: Array di prezzi
            period: Periodo per il calcolo dell'EMA
            
        Returns:
            np.ndarray: Array con i valori EMA
        """
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[period-1] = np.mean(data[:period])
        
        for i in range(period, len(data)):
            ema[i] = data[i] * alpha + ema[i-1] * (1 - alpha)
            
        return ema
        
    def calculate(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calcola i valori MACD.
        
        Args:
            data: DataFrame con colonna 'close' per i prezzi
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: 
                - MACD line (fast EMA - slow EMA)
                - Signal line (EMA del MACD)
                - Histogram (MACD - Signal)
                
        Raises:
            ValueError: Se manca la colonna 'close' nel DataFrame
        """
        if 'close' not in data.columns:
            logger.error("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        close_prices = data['close'].values
        
        # Calcola EMA veloce e lenta
        fast_ema = self._ema(close_prices, self.fast_period)
        slow_ema = self._ema(close_prices, self.slow_period)
        
        # Calcola MACD line
        macd_line = fast_ema - slow_ema
        
        # Calcola Signal line
        signal_line = self._ema(macd_line, self.signal_period)
        
        # Calcola Histogram
        histogram = macd_line - signal_line
        
        logger.debug(f"Calcolato MACD, ultimi valori: {macd_line[-5:]}")
        return macd_line, signal_line, histogram
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato su MACD.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            macd_line, signal_line, histogram = self.calculate(data)
            
            # Prendi gli ultimi due valori per il confronto
            curr_hist = histogram[-1]
            prev_hist = histogram[-2]
            
            # Calcola la forza del segnale basata sull'ampiezza dell'istogramma
            # e il cambio di direzione
            if curr_hist > 0 and prev_hist < 0:  # Crossover bullish
                strength = abs(curr_hist) / (abs(macd_line[-1]) + 1e-6)
                confidence = min(strength * 1.5, 1.0)  # Aumenta la confidenza ma limita a 1
                signal = 1 if confidence > self.signal_threshold else 0
                logger.info(f"MACD crossover bullish, confidence: {confidence:.2f}, signal: {signal}")
                return signal
                
            elif curr_hist < 0 and prev_hist > 0:  # Crossover bearish
                strength = abs(curr_hist) / (abs(macd_line[-1]) + 1e-6)
                confidence = min(strength * 1.5, 1.0)
                signal = -1 if confidence > self.signal_threshold else 0
                logger.info(f"MACD crossover bearish, confidence: {confidence:.2f}, signal: {signal}")
                return signal
                
            # Divergenze
            elif curr_hist > 0 and curr_hist > prev_hist:  # Momentum bullish
                confidence = min(curr_hist / (abs(macd_line[-1]) + 1e-6), 1.0)
                if confidence > self.signal_threshold:
                    logger.info(f"MACD momentum bullish, confidence: {confidence:.2f}")
                    return 0.5  # Segnale più debole per momentum
                    
            elif curr_hist < 0 and curr_hist < prev_hist:  # Momentum bearish
                confidence = min(abs(curr_hist) / (abs(macd_line[-1]) + 1e-6), 1.0)
                if confidence > self.signal_threshold:
                    logger.info(f"MACD momentum bearish, confidence: {confidence:.2f}")
                    return -0.5  # Segnale più debole per momentum
            
            logger.debug(f"MACD neutrale, nessun segnale")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale MACD: {str(e)}")
            return 0
