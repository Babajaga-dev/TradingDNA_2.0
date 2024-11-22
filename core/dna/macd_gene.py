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
        
    def _ema(self, data: np.ndarray, period: int, start_index: int = 0) -> np.ndarray:
        """Calcola l'EMA (Exponential Moving Average).
        
        Args:
            data: Array di prezzi
            period: Periodo per il calcolo dell'EMA
            start_index: Indice da cui iniziare il calcolo dell'EMA
            
        Returns:
            np.ndarray: Array con i valori EMA
        """
        if len(data) < period:
            return np.full_like(data, np.nan)
            
        alpha = 2 / (period + 1)
        ema = np.full_like(data, np.nan)
        
        # Calcola SMA iniziale
        valid_start = start_index + period - 1
        ema[valid_start] = np.mean(data[start_index:valid_start + 1])
        
        # Calcola EMA
        for i in range(valid_start + 1, len(data)):
            ema[i] = (data[i] * alpha) + (ema[i-1] * (1 - alpha))
            
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
            ValueError: Se manca la colonna 'close' nel DataFrame o non ci sono abbastanza dati
        """
        if 'close' not in data.columns:
            logger.error("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        min_periods = max(self.fast_period, self.slow_period) + self.signal_period
        if len(data) < min_periods:
            logger.error(f"Dati insufficienti per calcolare MACD. Richiesti almeno {min_periods} punti")
            raise ValueError(f"Sono necessari almeno {min_periods} punti per calcolare MACD")
            
        close_prices = data['close'].values
        
        # Calcola EMA veloce e lenta
        fast_ema = self._ema(close_prices, self.fast_period)
        slow_ema = self._ema(close_prices, self.slow_period)
        
        # Calcola MACD line
        macd_line = np.full_like(close_prices, np.nan)
        valid_macd_start = self.slow_period - 1
        macd_line[valid_macd_start:] = fast_ema[valid_macd_start:] - slow_ema[valid_macd_start:]
        
        # Calcola Signal line partendo dal punto in cui MACD è valido
        signal_line = self._ema(macd_line, self.signal_period, start_index=valid_macd_start)
        
        # Calcola Histogram
        histogram = macd_line - signal_line
        
        logger.debug(f"Calcolato MACD, ultimi valori: {macd_line[-5:]}")
        return macd_line, signal_line, histogram
        
    def _calculate_trend_strength(self, values: np.ndarray) -> float:
        """Calcola la forza del trend basata sulla sequenza di valori.
        
        Args:
            values: Array di valori da analizzare
            
        Returns:
            float: Forza del trend (positiva=rialzista, negativa=ribassista)
        """
        if len(values) < 2:
            return 0.0
            
        # Rimuovi NaN
        valid_values = values[~np.isnan(values)]
        if len(valid_values) < 2:
            return 0.0
            
        # Calcola le differenze consecutive
        diffs = np.diff(valid_values)
        
        # Calcola la media delle differenze
        avg_diff = np.mean(diffs)
        
        # Calcola la consistenza del trend (quante differenze hanno lo stesso segno)
        consistency = np.sum(np.sign(diffs) == np.sign(avg_diff)) / len(diffs)
        
        # Combina la media delle differenze con la consistenza
        strength = avg_diff * consistency
        
        return strength
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato su MACD.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            min_periods = max(self.fast_period, self.slow_period, self.signal_period)
            if len(data) < min_periods + 10:  # +10 per l'analisi del trend
                logger.warning(f"Dati insufficienti per generare segnale MACD")
                return 0
                
            macd_line, signal_line, histogram = self.calculate(data)
            
            # Verifica che ci siano abbastanza dati validi
            valid_data = ~np.isnan(macd_line) & ~np.isnan(signal_line) & ~np.isnan(histogram)
            if np.sum(valid_data) < 10:
                logger.warning("Dati validi insufficienti per l'analisi del trend")
                return 0
                
            # Prendi gli ultimi 10 valori validi
            last_macd = macd_line[valid_data][-10:]
            last_signal = signal_line[valid_data][-10:]
            last_hist = histogram[valid_data][-10:]
            last_prices = data['close'].values[valid_data][-10:]
            
            # Calcola la forza dei trend
            macd_strength = self._calculate_trend_strength(last_macd)
            price_strength = self._calculate_trend_strength(last_prices)
            hist_strength = self._calculate_trend_strength(last_hist)
            
            # Log dei valori per debug
            logger.debug(f"MACD strength: {macd_strength:.4f}")
            logger.debug(f"Price strength: {price_strength:.4f}")
            logger.debug(f"Histogram strength: {hist_strength:.4f}")
            
            # Calcola la forza complessiva del trend
            total_strength = (macd_strength + price_strength + hist_strength) / 3
            
            # Verifica trend rialzista
            if (total_strength > 0 and 
                last_macd[-1] > last_signal[-1] and
                last_hist[-1] > 0):
                logger.info(f"Trend rialzista rilevato, strength: {total_strength:.4f}")
                return 1
                
            # Verifica trend ribassista
            elif (total_strength < 0 and 
                  last_macd[-1] < last_signal[-1] and
                  last_hist[-1] < 0):
                logger.info(f"Trend ribassista rilevato, strength: {total_strength:.4f}")
                return -1
            
            logger.debug(f"Nessun trend significativo rilevato, strength: {total_strength:.4f}")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale MACD: {str(e)}")
            return 0
