"""Gene per il calcolo delle Bollinger Bands.

Questo modulo implementa il gene Bollinger che calcola e genera segnali
basati sulle bande di Bollinger.
"""
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from utils.logger_base import get_component_logger
from core.dna.gene import Gene  # Modificato l'import da base a gene

# Setup logger
logger = get_component_logger('BollingerGene')

class BollingerGene(Gene):
    """Gene per il calcolo delle Bollinger Bands."""
    
    def __init__(self) -> None:
        """Inizializza il gene Bollinger."""
        super().__init__("bollinger")
        self.period: int = self.params.get('period', 20)
        self.num_std: float = self.params.get('num_std', 2.0)
        self.signal_threshold: float = self.params.get('signal_threshold', 0.6)
        logger.info(f"Inizializzato Bollinger con periodo {self.period} e {self.num_std} deviazioni standard")
        
    def calculate(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calcola le Bollinger Bands.
        
        Args:
            data: DataFrame con colonna 'close' per i prezzi
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: 
                - Middle Band (SMA)
                - Upper Band
                - Lower Band
                
        Raises:
            ValueError: Se manca la colonna 'close' nel DataFrame
        """
        if 'close' not in data.columns:
            logger.error("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        close_prices = data['close'].values
        
        # Calcola la media mobile semplice (Middle Band)
        middle_band = np.zeros_like(close_prices)
        for i in range(self.period-1, len(close_prices)):
            middle_band[i] = np.mean(close_prices[i-self.period+1:i+1])
            
        # Calcola la deviazione standard
        std = np.zeros_like(close_prices)
        for i in range(self.period-1, len(close_prices)):
            std[i] = np.std(close_prices[i-self.period+1:i+1])
            
        # Calcola Upper e Lower Band
        upper_band = middle_band + (std * self.num_std)
        lower_band = middle_band - (std * self.num_std)
        
        logger.debug(f"Calcolate Bollinger Bands, ultimi valori MB: {middle_band[-5:]}")
        return middle_band, upper_band, lower_band
        
    def _calculate_bandwidth(self, middle: float, upper: float, lower: float) -> float:
        """Calcola la Bandwidth delle bande.
        
        Args:
            middle: Valore Middle Band
            upper: Valore Upper Band
            lower: Valore Lower Band
            
        Returns:
            float: Bandwidth percentuale
        """
        return (upper - lower) / middle if middle != 0 else 0
        
    def _calculate_percent_b(self, price: float, upper: float, lower: float) -> float:
        """Calcola il %B (posizione del prezzo rispetto alle bande).
        
        Args:
            price: Prezzo attuale
            upper: Valore Upper Band
            lower: Valore Lower Band
            
        Returns:
            float: Valore %B (0-1)
        """
        return (price - lower) / (upper - lower) if (upper - lower) != 0 else 0.5
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato sulle Bollinger Bands.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            float: Segnale di trading (-1=sell, 0=hold, 1=buy)
        """
        try:
            middle_band, upper_band, lower_band = self.calculate(data)
            current_price = data['close'].iloc[-1]
            
            # Calcola metriche
            bandwidth = self._calculate_bandwidth(
                middle_band[-1], upper_band[-1], lower_band[-1]
            )
            percent_b = self._calculate_percent_b(
                current_price, upper_band[-1], lower_band[-1]
            )
            
            # Trend della volatilità
            prev_bandwidth = self._calculate_bandwidth(
                middle_band[-2], upper_band[-2], lower_band[-2]
            )
            volatility_expanding = bandwidth > prev_bandwidth
            
            # Segnali di trading
            if current_price < lower_band[-1]:  # Prezzo sotto Lower Band
                # Calcola confidenza basata su quanto il prezzo è sotto la banda
                distance = (lower_band[-1] - current_price) / lower_band[-1] if lower_band[-1] != 0 else 0
                confidence = min(distance * 2, 1.0)  # Aumenta sensibilità ma limita a 1
                
                # Modifica confidenza basata su volatilità
                if volatility_expanding:
                    confidence *= 0.8  # Riduce confidenza se volatilità in aumento
                    
                signal = 1 if confidence > self.signal_threshold else 0
                logger.info(f"Bollinger oversold, confidence: {confidence:.2f}, signal: {signal}")
                return signal
                
            elif current_price > upper_band[-1]:  # Prezzo sopra Upper Band
                # Evita divisione per zero
                distance = (current_price - upper_band[-1]) / upper_band[-1] if upper_band[-1] != 0 else 0
                confidence = min(distance * 2, 1.0)
                
                if volatility_expanding:
                    confidence *= 0.8
                    
                signal = -1 if confidence > self.signal_threshold else 0
                logger.info(f"Bollinger overbought, confidence: {confidence:.2f}, signal: {signal}")
                return signal
                
            # Segnali di momentum basati su %B
            elif 0.05 < percent_b < 0.2 and not volatility_expanding:
                confidence = (0.2 - percent_b) / 0.15  # Scala tra 0-1
                if confidence > self.signal_threshold:
                    logger.info(f"Bollinger momentum bullish, confidence: {confidence:.2f}")
                    return 0.5
                    
            elif 0.8 < percent_b < 0.95 and not volatility_expanding:
                confidence = (percent_b - 0.8) / 0.15
                if confidence > self.signal_threshold:
                    logger.info(f"Bollinger momentum bearish, confidence: {confidence:.2f}")
                    return -0.5
            
            logger.debug(f"Bollinger neutrale, %B: {percent_b:.2f}, Bandwidth: {bandwidth:.2f}")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale Bollinger: {str(e)}")
            return 0
