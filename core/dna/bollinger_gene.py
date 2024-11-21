"""Gene per il calcolo delle Bollinger Bands.

Questo modulo implementa il gene Bollinger che calcola e genera segnali
basati sull'indicatore Bollinger Bands.
"""
from typing import Dict
import numpy as np
import pandas as pd
from utils.logger import get_component_logger
from core.dna.base import Gene

# Setup logger
logger = get_component_logger('BollingerGene')

class BollingerGene(Gene):
    """Gene per il calcolo delle Bollinger Bands."""
    
    def __init__(self) -> None:
        """Inizializza il gene Bollinger."""
        super().__init__("bollinger")
        self.period: int = self.params.get('period', 20)
        self.std_dev: float = self.params.get('std_dev', 2.0)
        self.signal_threshold: float = self.params.get('signal_threshold', 0.8)
        logger.info(
            f"Inizializzato Bollinger con periodo {self.period} e "
            f"deviazione {self.std_dev}"
        )
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Calcola le Bollinger Bands.
        
        Args:
            data: DataFrame con colonna 'close' per i prezzi
            
        Returns:
            Dict[str, np.ndarray]: Dictionary con:
                - middle: media mobile
                - upper: banda superiore
                - lower: banda inferiore
                
        Raises:
            ValueError: Se manca la colonna 'close' nel DataFrame
        """
        if 'close' not in data.columns:
            logger.error("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        close = data['close'].values
        middle = pd.Series(close).rolling(window=self.period).mean()
        std = pd.Series(close).rolling(window=self.period).std()
        upper = middle + (std * self.std_dev)
        lower = middle - (std * self.std_dev)
        
        logger.debug(
            f"Calcolate Bollinger Bands, ultimi valori: "
            f"Upper={upper[-1]:.2f}, Middle={middle[-1]:.2f}, "
            f"Lower={lower[-1]:.2f}"
        )
        
        return {
            'middle': middle.values,
            'upper': upper.values,
            'lower': lower.values
        }
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato su Bollinger Bands.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            bands = self.calculate(data)
            close = data['close'].values[-1]
            
            # Calcola %B ((price - lower)/(upper - lower))
            upper = bands['upper'][-1]
            lower = bands['lower'][-1]
            band_width = upper - lower
            
            if band_width == 0:
                logger.warning("Bandwidth zero, nessun segnale generato")
                return 0
                
            b_value = (close - lower) / band_width
            
            if b_value < (1 - self.signal_threshold):
                logger.info(
                    f"Prezzo vicino alla banda inferiore (%B: {b_value:.2f}), "
                    f"signal: 1"
                )
                return 1
                
            elif b_value > self.signal_threshold:
                logger.info(
                    f"Prezzo vicino alla banda superiore (%B: {b_value:.2f}), "
                    f"signal: -1"
                )
                return -1
                
            logger.debug(f"Prezzo nella banda centrale (%B: {b_value:.2f})")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale Bollinger: {str(e)}")
            return 0
