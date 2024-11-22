"""Gene per l'analisi del Volume.

Questo modulo implementa il gene Volume che calcola e genera segnali
basati sull'analisi del volume degli scambi.
"""
from typing import Dict, Tuple, Any, Optional
import numpy as np
import pandas as pd
from utils.logger_base import get_component_logger
from utils.config import load_config
from core.dna.gene import Gene

# Setup logger
logger = get_component_logger('VolumeGene')

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
            
        self.params = {
            'vwap_period': config.get('vwap_period', 20),
            'volume_ma_period': config.get('volume_ma_period', 20),
            'signal_threshold': config.get('signal_threshold', 0.1),
            'weight': config.get('weight', 1.0)
        }
        
        logger.info(f"Inizializzato Volume con parametri: {self.params}")
        
    def calculate(self, data: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calcola gli indicatori di volume.
        
        Args:
            data: DataFrame con colonne OHLCV
            params: Parametri opzionali da usare invece di self.params
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: 
                - VWAP (Volume Weighted Average Price)
                - Volume MA (Media mobile del volume)
                - OBV (On Balance Volume)
                
        Raises:
            ValueError: Se mancano le colonne OHLCV o non ci sono abbastanza dati
        """
        if params is None:
            params = self.params
            
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logger.error("Colonne OHLCV mancanti nel DataFrame")
            raise ValueError("DataFrame deve contenere le colonne OHLCV")
            
        if len(data) < max(params['vwap_period'], params['volume_ma_period']):
            logger.error(f"Dati insufficienti per calcolare gli indicatori di volume")
            raise ValueError(f"Sono necessari almeno {max(params['vwap_period'], params['volume_ma_period'])} punti")
            
        # Calcola VWAP
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        cumulative_tp_vol = typical_price * data['volume']
        cumulative_vol = data['volume']
        
        vwap_values = np.zeros(len(data))
        for i in range(len(data)):
            start_idx = max(0, i - params['vwap_period'] + 1)
            vwap_values[i] = (cumulative_tp_vol.iloc[start_idx:i+1].sum() / 
                            cumulative_vol.iloc[start_idx:i+1].sum())
                
        # Calcola Volume MA usando rolling window
        volume_ma = data['volume'].rolling(window=params['volume_ma_period'], min_periods=1).mean()
            
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
        
        logger.debug(f"Calcolati indicatori volume, ultimi valori VWAP: {vwap_values[-5:]}")
        return vwap_values, volume_ma.to_numpy(), obv_values
        
    def generate_signal(self, data: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> float:
        """Genera segnale di trading basato sul volume.
        
        Args:
            data: DataFrame con dati OHLCV
            params: Parametri opzionali da usare invece di self.params
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        if params is None:
            params = self.params
            
        try:
            if len(data) < max(params['vwap_period'], params['volume_ma_period']):
                logger.warning("Dati insufficienti per generare segnale volume")
                return 0.0
                
            vwap, volume_ma, obv = self.calculate(data, params)
            
            # Analisi VWAP e Volume
            price = data['close'].iloc[-1]
            current_volume = data['volume'].iloc[-1]
            
            # Calcola la forza del segnale
            price_distance = abs(price - vwap[-1]) / vwap[-1]
            volume_strength = (current_volume - volume_ma[-1]) / volume_ma[-1]
            
            # Normalizza la forza del segnale tra 0 e 1
            signal_strength = min(1.0, (price_distance + volume_strength) / 2)
            
            # Applica threshold
            if signal_strength < params['signal_threshold']:
                logger.debug("Segnale sotto threshold")
                return 0.0
            
            if price > vwap[-1] and current_volume > volume_ma[-1]:
                logger.info(f"Segnale rialzista: prezzo sopra VWAP con volume alto")
                return signal_strength * params['weight']
            elif price < vwap[-1] and current_volume > volume_ma[-1]:
                logger.info(f"Segnale ribassista: prezzo sotto VWAP con volume alto")
                return -signal_strength * params['weight']
                
            logger.debug("Volume neutrale")
            return 0.0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale Volume: {str(e)}")
            return 0.0
            
    def optimize_params(self, data: pd.DataFrame) -> None:
        """Ottimizza i parametri del gene Volume.
        
        Args:
            data: DataFrame con dati OHLCV
        """
        # Carica range parametri da config
        config = load_config('dna.yaml')
        opt_config = config['optimization']['volume']
        
        vwap_range = opt_config['vwap_period']
        volume_ma_range = opt_config['volume_ma_period']
        threshold_range = opt_config['signal_threshold']
        
        best_sharpe = -np.inf
        best_params = self.params.copy()
        
        # Calcola returns una volta sola
        returns = np.diff(data['close']) / data['close'].iloc[:-1]
        
        for vwap_p in range(vwap_range[0], vwap_range[1], 2):
            for vol_p in range(volume_ma_range[0], volume_ma_range[1], 2):
                for threshold in np.arange(threshold_range[0], threshold_range[1], 0.1):
                    test_params = {
                        'vwap_period': vwap_p,
                        'volume_ma_period': vol_p,
                        'signal_threshold': threshold,
                        'weight': self.params['weight']
                    }
                    
                    try:
                        # Genera segnali per l'intero dataset usando i parametri di test
                        signals = np.zeros(len(data))
                        for i in range(max(vwap_p, vol_p), len(data)):
                            signals[i] = self.generate_signal(data.iloc[:i+1], test_params)
                        
                        # Calcola metriche usando i segnali shiftati
                        strategy_returns = returns * signals[:-1]  # Allinea i segnali con i returns
                        if len(strategy_returns) > 0 and np.std(strategy_returns) > 0:
                            sharpe = np.mean(strategy_returns) / np.std(strategy_returns)
                            
                            if sharpe > best_sharpe:
                                best_sharpe = sharpe
                                best_params = test_params.copy()
                                
                    except Exception as e:
                        logger.error(f"Errore durante l'ottimizzazione: {str(e)}")
                        continue
        
        # Applica i migliori parametri
        if best_params != self.params:
            self.params = best_params
            logger.info(f"Parametri ottimizzati: {self.params}")
        else:
            logger.info("Nessun miglioramento trovato durante l'ottimizzazione")
