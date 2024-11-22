"""Gene per il calcolo del Relative Strength Index.

Questo modulo implementa il gene RSI che calcola e genera segnali
basati sull'indicatore Relative Strength Index.
"""
from typing import Dict
import numpy as np
import pandas as pd
from utils.logger_base import get_component_logger
from core.dna.gene import Gene

# Setup logger
logger = get_component_logger('RSIGene')

class RSIGene(Gene):
    """Gene per il calcolo del Relative Strength Index."""
    
    def __init__(self) -> None:
        """Inizializza il gene RSI."""
        super().__init__("rsi")
        self.period: int = self.params.get('period', 14)
        self.overbought: float = self.params.get('overbought', 70)
        self.oversold: float = self.params.get('oversold', 30)
        self.signal_threshold: float = self.params.get('signal_threshold', 0.6)
        logger.info(f"Inizializzato RSI con periodo {self.period}")
        
    def calculate(self, data: pd.DataFrame) -> np.ndarray:
        """Calcola i valori RSI.
        
        Args:
            data: DataFrame con colonna 'close' per i prezzi
            
        Returns:
            np.ndarray: Array con i valori RSI
            
        Raises:
            ValueError: Se manca la colonna 'close' nel DataFrame
        """
        if 'close' not in data.columns:
            logger.error("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        close_prices = data['close'].values
        deltas = np.diff(close_prices)
        seed = deltas[:self.period+1]
        up = seed[seed >= 0].sum()/self.period
        down = -seed[seed < 0].sum()/self.period
        rs = up/down if down != 0 else 0
        rsi = np.zeros_like(close_prices)
        rsi[self.period] = 100 - 100/(1+rs)

        for i in range(self.period+1, len(close_prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0
            else:
                upval = 0
                downval = -delta
                
            up = (up*(self.period-1) + upval)/self.period
            down = (down*(self.period-1) + downval)/self.period
            rs = up/down if down != 0 else 0
            rsi[i] = 100 - 100/(1+rs)
            
        logger.debug(f"Calcolato RSI, ultimi valori: {rsi[-5:]}")
        return rsi
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato su RSI.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            rsi = self.calculate(data)
            current_rsi = rsi[-1]
            
            if current_rsi < self.oversold and current_rsi < rsi[-2]:
                confidence = (self.oversold - current_rsi)/(self.oversold)
                signal = 1 if confidence > self.signal_threshold else 0
                logger.info(f"RSI oversold ({current_rsi:.2f}), confidence: {confidence:.2f}, signal: {signal}")
                return signal
                
            elif current_rsi > self.overbought and current_rsi > rsi[-2]:
                confidence = (current_rsi - self.overbought)/(100 - self.overbought)
                signal = -1 if confidence > self.signal_threshold else 0
                logger.info(f"RSI overbought ({current_rsi:.2f}), confidence: {confidence:.2f}, signal: {signal}")
                return signal
                
            logger.debug(f"RSI neutrale ({current_rsi:.2f}), nessun segnale")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale RSI: {str(e)}")
            return 0
