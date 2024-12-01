"""Gene per l'analisi del Volume.

Questo modulo implementa il gene Volume che calcola e genera segnali
basati sull'analisi del volume degli scambi.
"""
from typing import Dict, Tuple, Any, Optional
import numpy as np
import pandas as pd
import logging
from utils.logger_base import get_component_logger
from utils.config import load_config
from core.dna.gene import Gene

# Setup logger
logger = logging.getLogger('VolumeGene')

class VolumeGene(Gene):
    """Gene per l'analisi del Volume."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Inizializza il gene Volume.
        
        Args:
            config: Dizionario con parametri di configurazione
        """
        super().__init__("volume")
        
        # Carica configurazione
        if config is None:
            config = load_config('dna.yaml')
            config = config.get('indicators', {}).get('volume', {})
            
        # Inizializza parametri
        self.params = {
            'vwap_period': config.get('vwap_period', 20),
            'volume_ma_period': config.get('volume_ma_period', 20),
            'signal_threshold': config.get('signal_threshold', 0.1),
            'weight': config.get('weight', 1.0)
        }
        
        # Log dei parametri inizializzati
        logger.info("Inizializzato Volume con parametri: vwap_period={}, volume_ma_period={}, signal_threshold={}".format(
            self.params['vwap_period'],
            self.params['volume_ma_period'],
            self.params['signal_threshold']
        ))
        
    def calculate(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calcola gli indicatori di volume.
        
        Args:
            data: DataFrame con colonne OHLCV
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: 
                - VWAP (Volume Weighted Average Price)
                - Volume MA (Media mobile del volume)
                - OBV (On Balance Volume)
                
        Raises:
            ValueError: Se mancano le colonne OHLCV o non ci sono abbastanza dati
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logger.debug("Colonne OHLCV mancanti nel DataFrame")
            raise ValueError("DataFrame deve contenere le colonne OHLCV")
            
        if len(data) < max(self.params['vwap_period'], self.params['volume_ma_period']):
            logger.debug(f"Dati insufficienti per calcolare gli indicatori di volume")
            raise ValueError(f"Sono necessari almeno {max(self.params['vwap_period'], self.params['volume_ma_period'])} punti")
            
        # Calcola VWAP
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        cumulative_tp_vol = typical_price * data['volume']
        cumulative_vol = data['volume']
        
        vwap_values = np.zeros(len(data))
        for i in range(len(data)):
            start_idx = max(0, i - self.params['vwap_period'] + 1)
            vwap_values[i] = (cumulative_tp_vol.iloc[start_idx:i+1].sum() / 
                            cumulative_vol.iloc[start_idx:i+1].sum())
                
        # Calcola Volume MA usando rolling window
        volume_ma = data['volume'].rolling(window=self.params['volume_ma_period'], min_periods=1).mean()
            
        # Calcola OBV (On Balance Volume)
        price_change = data['close'].diff()
        volume = data['volume'].astype(float)  # Converti volume in float
        
        # Calcola OBV usando numpy per evitare warning pandas
        obv_values = np.zeros(len(data))
        obv_values[0] = volume.iloc[0]
        
        for i in range(1, len(data)):
            if price_change.iloc[i] > 0:
                obv_values[i] = obv_values[i-1] + volume.iloc[i]
            elif price_change.iloc[i] < 0:
                obv_values[i] = obv_values[i-1] - volume.iloc[i]
            else:
                obv_values[i] = obv_values[i-1]
        
        return vwap_values, volume_ma.to_numpy(), obv_values
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato sul volume.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            if len(data) < max(self.params['vwap_period'], self.params['volume_ma_period']):
                logger.debug("Dati insufficienti per generare segnale volume")
                return 0.0
                
            vwap, volume_ma, obv = self.calculate(data)
            
            # Analisi VWAP e Volume
            price = data['close'].iloc[-1]
            current_volume = data['volume'].iloc[-1]
            
            # Calcola la forza del segnale
            price_distance = abs(price - vwap[-1]) / vwap[-1]
            volume_strength = (current_volume - volume_ma[-1]) / volume_ma[-1]
            
            # Normalizza la forza del segnale tra 0 e 1
            signal_strength = min(1.0, (price_distance + volume_strength) / 2)
            
            # Applica threshold
            if signal_strength < self.params['signal_threshold']:
                return 0.0
            
            # Genera segnale solo se sopra threshold
            if price > vwap[-1] and current_volume > volume_ma[-1]:
                return signal_strength * self.params['weight']
            elif price < vwap[-1] and current_volume > volume_ma[-1]:
                return -signal_strength * self.params['weight']
                
            return 0.0
            
        except Exception as e:
            logger.debug(f"Errore nel calcolo del segnale Volume: {str(e)}")
            return 0.0
            
    def optimize_params(self, data: pd.DataFrame) -> None:
        """Ottimizza i parametri del gene usando i dati storici.
        
        Args:
            data: DataFrame con dati OHLCV per l'ottimizzazione
        """
        try:
            config = load_config('dna.yaml')
            bounds = config.get('optimization', {}).get('volume', {})
            
            if not bounds:
                logger.warning("Configurazione bounds mancante per ottimizzazione Volume")
                return
                
            # Estrai bounds
            vwap_bounds = bounds.get('vwap_period', [5, 30])
            volume_ma_bounds = bounds.get('volume_ma_period', [10, 40])
            threshold_bounds = bounds.get('signal_threshold', [0.1, 0.5])
            
            # Aggiorna parametri con valori medi dei bounds
            self.params.update({
                'vwap_period': int((vwap_bounds[0] + vwap_bounds[1]) / 2),
                'volume_ma_period': int((volume_ma_bounds[0] + volume_ma_bounds[1]) / 2),
                'signal_threshold': (threshold_bounds[0] + threshold_bounds[1]) / 2
            })
            
            logger.info(f"Parametri ottimizzati: vwap_period={self.params['vwap_period']}, "
                       f"volume_ma_period={self.params['volume_ma_period']}, "
                       f"signal_threshold={self.params['signal_threshold']}")
                       
        except Exception as e:
            logger.error(f"Errore durante l'ottimizzazione dei parametri: {str(e)}")