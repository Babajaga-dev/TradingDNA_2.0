"""Gene per l'analisi del volume.

Questo modulo implementa il gene Volume che calcola e genera segnali
basati sull'analisi del volume degli scambi.
"""
from typing import Dict
import numpy as np
import pandas as pd
from utils.logger import get_component_logger
from core.dna.base import Gene

# Setup logger
logger = get_component_logger('VolumeGene')

class VolumeGene(Gene):
    """Gene per l'analisi del volume degli scambi."""
    
    def __init__(self) -> None:
        """Inizializza il gene Volume."""
        super().__init__("volume")
        self.period: int = self.params.get('period', 20)
        self.threshold: float = self.params.get('threshold', 1.5)
        self.ma_type: str = self.params.get('ma_type', 'sma')
        logger.info(
            f"Inizializzato Volume con periodo {self.period}, "
            f"threshold {self.threshold}, MA type {self.ma_type}"
        )
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Calcola metriche sul volume.
        
        Args:
            data: DataFrame con colonne 'volume' e 'close'
            
        Returns:
            Dict[str, np.ndarray]: Dictionary con:
                - volume_ma: media mobile dei volumi
                - volume_ratio: ratio volume corrente/media mobile
                
        Raises:
            ValueError: Se mancano le colonne necessarie nel DataFrame
        """
        required_columns = ['volume', 'close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            logger.error(f"Colonne mancanti nel DataFrame: {missing_columns}")
            raise ValueError(
                f"DataFrame deve contenere le colonne: {required_columns}"
            )
            
        volume = data['volume'].values
        
        # Calcola media mobile in base al tipo specificato
        if self.ma_type == 'ema':
            volume_ma = pd.Series(volume).ewm(span=self.period, adjust=False).mean()
        else:  # default: sma
            volume_ma = pd.Series(volume).rolling(window=self.period).mean()
            
        # Calcola volume ratio (volume corrente / media mobile)
        volume_ratio = np.zeros_like(volume)
        valid_ma = volume_ma > 0  # evita divisione per zero
        volume_ratio[valid_ma] = volume[valid_ma] / volume_ma[valid_ma]
        
        logger.debug(
            f"Calcolate metriche volume, ultimi valori: "
            f"Volume={volume[-1]:.0f}, MA={volume_ma[-1]:.0f}, "
            f"Ratio={volume_ratio[-1]:.2f}"
        )
        
        return {
            'volume_ma': volume_ma.values,
            'volume_ratio': volume_ratio
        }
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato sul volume.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            metrics = self.calculate(data)
            volume_ratio = metrics['volume_ratio'][-1]
            
            # Calcola variazione prezzo
            close = data['close'].values
            price_change = close[-1] - close[-2]
            price_change_pct = (price_change / close[-2]) * 100
            
            if volume_ratio > self.threshold:
                if price_change > 0:
                    logger.info(
                        f"Volume spike rialzista (ratio: {volume_ratio:.2f}, "
                        f"Δ price: {price_change_pct:.2f}%), signal: 1"
                    )
                    return 1
                else:
                    logger.info(
                        f"Volume spike ribassista (ratio: {volume_ratio:.2f}, "
                        f"Δ price: {price_change_pct:.2f}%), signal: -1"
                    )
                    return -1
                    
            logger.debug(
                f"Volume nella norma (ratio: {volume_ratio:.2f}, "
                f"Δ price: {price_change_pct:.2f}%)"
            )
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale Volume: {str(e)}")
            return 0
