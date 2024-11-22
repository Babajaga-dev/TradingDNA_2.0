"""Gene per il calcolo del Relative Strength Index.

Questo modulo implementa il gene RSI che calcola e genera segnali
basati sull'indicatore Relative Strength Index.
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from utils.logger_base import get_component_logger
from core.dna.gene import Gene

# Setup logger
logger = get_component_logger('RSIGene')

class RSIGene(Gene):
    """Gene per il calcolo del Relative Strength Index."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Inizializza il gene RSI.
        
        Args:
            config: Dizionario con parametri di configurazione
        """
        super().__init__("rsi")
        
        # Carica configurazione con valori di default
        if config is None:
            config = {}
            
        self.period: int = config.get('period', 14)
        self.overbought: float = config.get('overbought', 70)
        self.oversold: float = config.get('oversold', 30)
        self.signal_threshold: float = config.get('signal_threshold', 0.6)
        self.weight: float = config.get('weight', 1.0)
        
        logger.info(f"Inizializzato RSI con periodo {self.period}")
        
    def calculate(self, data: pd.DataFrame) -> np.ndarray:
        """Calcola i valori RSI.
        
        Args:
            data: DataFrame con colonna 'close' per i prezzi
            
        Returns:
            np.ndarray: Array con i valori RSI
            
        Raises:
            ValueError: Se manca la colonna 'close' nel DataFrame o se non ci sono abbastanza dati
        """
        if 'close' not in data.columns:
            logger.error("Colonna 'close' mancante nel DataFrame")
            raise ValueError("DataFrame deve contenere la colonna 'close'")
            
        if len(data) < self.period + 1:
            logger.error(f"Dati insufficienti per calcolare RSI. Richiesti almeno {self.period + 1} punti")
            raise ValueError(f"Sono necessari almeno {self.period + 1} punti per calcolare RSI")
            
        # Calcola le variazioni di prezzo
        prices = data['close'].values
        changes = np.diff(prices)
        
        # Separa gains e losses
        gains = np.maximum(changes, 0)
        losses = -np.minimum(changes, 0)
        
        # Inizializza array RSI
        rsi = np.full_like(prices, np.nan)
        
        # Calcola la prima media con controllo per divisione per zero
        avg_gain = np.mean(gains[:self.period]) if len(gains) >= self.period else 0
        avg_loss = np.mean(losses[:self.period]) if len(losses) >= self.period else 0
        
        # Gestione caso speciale per avg_loss = 0
        if avg_loss == 0:
            rsi[self.period] = 100 if avg_gain > 0 else 50
        else:
            rs = avg_gain / avg_loss
            rsi[self.period] = 100 - (100 / (1 + rs))
            
        # Calcola i successivi RSI
        for i in range(self.period + 1, len(prices)):
            avg_gain = (avg_gain * (self.period - 1) + gains[i-1]) / self.period
            avg_loss = (avg_loss * (self.period - 1) + losses[i-1]) / self.period
            
            if avg_loss == 0:
                rsi[i] = 100 if avg_gain > 0 else 50
            else:
                rs = avg_gain / avg_loss
                rsi[i] = 100 - (100 / (1 + rs))
                
        # Riempi i primi valori con la media mobile
        rsi[:self.period] = np.nanmean(rsi[self.period:self.period*2])
        
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
            if len(data) < self.period + 1:
                logger.warning("Dati insufficienti per generare segnale RSI")
                return 0
                
            rsi = self.calculate(data)
            current_rsi = rsi[-1]
            
            if np.isnan(current_rsi):
                logger.warning("RSI corrente è NaN, nessun segnale generato")
                return 0
            
            if current_rsi < self.oversold:
                confidence = (self.oversold - current_rsi)/(self.oversold)
                signal = 1 if confidence > self.signal_threshold else 0
                logger.info(f"RSI oversold ({current_rsi:.2f}), confidence: {confidence:.2f}, signal: {signal}")
                return signal * self.weight
                
            elif current_rsi > self.overbought:
                confidence = (current_rsi - self.overbought)/(100 - self.overbought)
                signal = -1 if confidence > self.signal_threshold else 0
                logger.info(f"RSI overbought ({current_rsi:.2f}), confidence: {confidence:.2f}, signal: {signal}")
                return signal * self.weight
                
            logger.debug(f"RSI neutrale ({current_rsi:.2f}), nessun segnale")
            return 0
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del segnale RSI: {str(e)}")
            return 0
