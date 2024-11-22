"""Gene per l'analisi del Volume.

Questo modulo implementa il gene Volume che calcola e genera segnali
basati sull'analisi del volume degli scambi.
"""
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from utils.logger_base import get_component_logger
from core.dna.gene import Gene

# Setup logger
logger = get_component_logger('VolumeGene')

def safe_divide(a, b, default=0):
    """Divisione sicura per evitare divisioni per zero."""
    return a / b if b != 0 else default

class VolumeGene(Gene):
    """Gene per l'analisi del Volume."""
    
    def __init__(self) -> None:
        """Inizializza il gene Volume."""
        super().__init__("volume")
        self.vwap_period: int = self.params.get('vwap_period', 14)
        self.volume_ma_period: int = self.params.get('volume_ma_period', 20)
        self.price_volume_ma_period: int = self.params.get('price_volume_ma_period', 30)
        self.signal_threshold: float = self.params.get('signal_threshold', 0.6)
        logger.info(f"Inizializzato Volume con periodi VWAP:{self.vwap_period}, Vol MA:{self.volume_ma_period}")
        
    def calculate(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calcola gli indicatori di volume.
        
        Args:
            data: DataFrame con colonne OHLCV
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]:
                - VWAP (Volume Weighted Average Price)
                - Volume MA
                - OBV (On Balance Volume)
                
        Raises:
            ValueError: Se mancano colonne necessarie nel DataFrame
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logger.error("Colonne OHLCV mancanti nel DataFrame")
            raise ValueError("DataFrame deve contenere le colonne OHLCV")
            
        # Calcola VWAP
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap = np.zeros(len(data))
        
        for i in range(self.vwap_period-1, len(data)):
            price_vol = typical_price.iloc[i-self.vwap_period+1:i+1] * data['volume'].iloc[i-self.vwap_period+1:i+1]
            volume = data['volume'].iloc[i-self.vwap_period+1:i+1]
            vwap[i] = np.sum(price_vol) / np.sum(volume)
            
        # Calcola Volume MA
        volume_ma = np.zeros(len(data))
        for i in range(self.volume_ma_period-1, len(data)):
            volume_ma[i] = np.mean(data['volume'].iloc[i-self.volume_ma_period+1:i+1])
            
        # Calcola OBV (On Balance Volume)
        close_diff = data['close'].diff()
        obv = np.zeros(len(data))
        
        for i in range(1, len(data)):
            if close_diff.iloc[i] > 0:
                obv[i] = obv[i-1] + data['volume'].iloc[i]
            elif close_diff.iloc[i] < 0:
                obv[i] = obv[i-1] - data['volume'].iloc[i]
            else:
                obv[i] = obv[i-1]
                
        logger.debug(f"Calcolati indicatori volume, ultimi VWAP: {vwap[-5:]}")
        return vwap, volume_ma, obv
        
    def _calculate_price_volume_trend(self, data: pd.DataFrame) -> float:
        """Calcola il trend prezzo-volume.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Indicatore di trend (-1 a 1)
        """
        period = self.price_volume_ma_period
        if len(data) < period:
            return 0
            
        # Calcola variazioni percentuali
        price_changes = data['close'].pct_change().iloc[-period:]
        volume_changes = data['volume'].pct_change().iloc[-period:]
        
        # Calcola correlazione
        try:
            correlation = np.corrcoef(price_changes, volume_changes)[0,1]
            return correlation if not np.isnan(correlation) else 0
        except Exception:
            return 0
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato sul volume.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            vwap, volume_ma, obv = self.calculate(data)
            
            current_price = data['close'].iloc[-1]
            current_volume = data['volume'].iloc[-1]
            
            # Analisi trend prezzo-volume
            pv_trend = self._calculate_price_volume_trend(data)
            
            # Volume spike analysis con divisione sicura
            volume_ratio = safe_divide(current_volume, volume_ma[-1], default=1)
            
            # VWAP analysis con divisione sicura
            vwap_ratio = safe_divide(current_price, vwap[-1], default=1)
            
            # OBV trend
            obv_trend = safe_divide(obv[-1] - obv[-2], abs(obv[-2]), default=0)
            
            # Segnali di trading
            if volume_ratio > 2.0:  # Volume spike significativo
                if current_price > vwap[-1] and pv_trend > 0:  # Conferma rialzista
                    confidence = min(volume_ratio/4 + abs(pv_trend), 1.0)
                    signal = 1 if confidence > self.signal_threshold else 0
                    logger.info(f"Volume spike rialzista, confidence: {confidence:.2f}, signal: {signal}")
                    return signal
                    
                elif current_price < vwap[-1] and pv_trend < 0:  # Conferma ribassista
                    confidence = min(volume_ratio/4 + abs(pv_trend), 1.0)
                    signal = -1 if confidence > self.signal_threshold else 0
                    logger.info(f"Volume spike ribassista, confidence: {confidence:.2f}, signal: {signal}")
                    return signal
                    
            # Segnali di momentum basati su OBV
            elif abs(obv_trend) > 0.02:  # Movimento significativo OBV
                if obv_trend > 0 and vwap_ratio > 1:
                    confidence = min(abs(obv_trend) * 20, 1.0)
                    if confidence > self.signal_threshold:
                        logger.info(f"OBV momentum rialzista, confidence: {confidence:.2f}")
                        return 0.5
                        
                elif obv_trend < 0 and vwap_ratio < 1:
                    confidence = min(abs(obv_trend) * 20, 1.0)
                    if confidence > self.signal_threshold:
                        logger.info(f"OBV momentum ribassista, confidence: {confidence:.2f}")
                        return -0.5
            
            logger.debug(f"Volume neutrale, ratio: {volume_ratio:.2f}, PV trend: {pv_trend:.2f}")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale Volume: {str(e)}")
            return 0
