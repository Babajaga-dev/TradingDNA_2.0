"""Pattern Recognition System per DNA.

Questo modulo implementa il sistema di riconoscimento pattern:
- Identificazione pattern ricorrenti
- Analisi serie temporali
- Correlazione pattern-risultati
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass

from .base import Gene
from utils.logger import get_component_logger

# Setup logger
logger = get_component_logger('PatternRecognition')

@dataclass
class Pattern:
    """Struttura dati per pattern identificati."""
    
    sequence: np.ndarray
    start_idx: int
    end_idx: int
    confidence: float
    correlation: float
    quality_score: float

class PatternRecognition(Gene):
    """Sistema di riconoscimento pattern di mercato."""
    
    def __init__(self):
        """Inizializza il sistema di pattern recognition."""
        super().__init__('pattern_recognition')
        
        # Pattern storage
        self.patterns: List[Pattern] = []
        self.min_pattern_length = self.params.get('min_pattern_length', 5)
        self.max_pattern_length = self.params.get('max_pattern_length', 20)
        self.min_confidence = self.params.get('min_confidence', 0.7)
        
        logger.info(f"Inizializzato Pattern Recognition con parametri: {self.params}")
        
    def calculate(self, data: pd.DataFrame) -> np.ndarray:
        """Calcola i pattern sulla serie temporale.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            Array con score di pattern per ogni punto
        """
        if len(data) < self.min_pattern_length:
            return np.zeros(len(data))
            
        # Normalizza prezzi per confronto pattern
        prices = self._normalize_prices(data['close'].values)
        pattern_scores = np.zeros(len(prices))
        
        # Identifica pattern per diverse lunghezze
        for length in range(self.min_pattern_length, min(self.max_pattern_length, len(prices))):
            current_pattern = prices[-length:]
            
            # Cerca pattern simili nella storia
            for i in range(len(prices) - length):
                historical_pattern = prices[i:i+length]
                similarity = self._calculate_similarity(current_pattern, historical_pattern)
                
                if similarity > self.min_confidence:
                    # Calcola correlazione con rendimenti futuri
                    future_correlation = self._calculate_future_correlation(
                        data, i+length, len(prices)-length)
                    
                    # Calcola quality score
                    quality = self._calculate_pattern_quality(
                        similarity, future_correlation, length)
                    
                    pattern = Pattern(
                        sequence=historical_pattern,
                        start_idx=i,
                        end_idx=i+length,
                        confidence=similarity,
                        correlation=future_correlation,
                        quality_score=quality
                    )
                    self.patterns.append(pattern)
                    pattern_scores[i:i+length] = max(pattern_scores[i:i+length], quality)
        
        return pattern_scores
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale di trading basato sui pattern.
        
        Args:
            data: DataFrame con dati OHLCV
            
        Returns:
            Segnale di trading: -1 (sell), 0 (hold), 1 (buy)
        """
        if len(data) < self.min_pattern_length:
            return 0
            
        # Calcola pattern scores
        pattern_scores = self.calculate(data)
        
        if not len(self.patterns):
            return 0
            
        # Analizza ultimi pattern identificati
        recent_patterns = [p for p in self.patterns 
                         if p.end_idx > len(data) - self.max_pattern_length]
                         
        if not recent_patterns:
            return 0
            
        # Calcola segnale composito
        signal = 0
        total_weight = 0
        
        for pattern in recent_patterns:
            # Peso basato su qualità e correlazione
            weight = pattern.quality_score * abs(pattern.correlation)
            signal += np.sign(pattern.correlation) * weight
            total_weight += weight
            
        return np.clip(signal / total_weight if total_weight > 0 else 0, -1, 1)
        
    def _normalize_prices(self, prices: np.ndarray) -> np.ndarray:
        """Normalizza i prezzi per confronto pattern."""
        return (prices - np.mean(prices)) / np.std(prices)
        
    def _calculate_similarity(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Calcola similarità tra due pattern."""
        correlation = np.corrcoef(pattern1, pattern2)[0, 1]
        return abs(correlation) if not np.isnan(correlation) else 0
        
    def _calculate_future_correlation(self, data: pd.DataFrame, 
                                   start_idx: int, length: int) -> float:
        """Calcola correlazione con rendimenti futuri."""
        if start_idx + length >= len(data):
            return 0
            
        future_returns = data['close'].pct_change().values[start_idx:start_idx+length]
        pattern_returns = data['close'].pct_change().values[start_idx-length:start_idx]
        
        correlation = np.corrcoef(pattern_returns, future_returns)[0, 1]
        return correlation if not np.isnan(correlation) else 0
        
    def _calculate_pattern_quality(self, similarity: float, 
                                correlation: float, length: float) -> float:
        """Calcola score qualità del pattern."""
        # Normalizza lunghezza
        length_factor = 1 - (length - self.min_pattern_length) / (
            self.max_pattern_length - self.min_pattern_length)
            
        # Combina metriche
        return (similarity * 0.4 + 
                abs(correlation) * 0.4 + 
                length_factor * 0.2)
