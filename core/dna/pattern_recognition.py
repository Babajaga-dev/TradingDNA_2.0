"""Pattern Recognition DNA.

Questo modulo implementa il riconoscimento di pattern nei prezzi
attraverso tecniche di normalizzazione e correlazione.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import List
from core.dna.gene import BaseGene

@dataclass
class Pattern:
    """Rappresenta un pattern identificato nella serie storica."""
    sequence: np.ndarray
    start_idx: int
    end_idx: int
    confidence: float
    correlation: float
    quality_score: float

class PatternRecognition(BaseGene):
    """Gene per il riconoscimento di pattern nei prezzi."""
    
    def __init__(self) -> None:
        """Inizializza il gene di pattern recognition."""
        super().__init__("pattern_recognition")
        self.min_pattern_length = 5
        self.max_pattern_length = 20
        self.min_confidence = 0.7
        self.patterns: List[Pattern] = []
        
    def _normalize_prices(self, prices: np.ndarray) -> np.ndarray:
        """Normalizza i prezzi usando z-score."""
        return (prices - np.mean(prices)) / np.std(prices)
        
    def _calculate_similarity(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Calcola la similarità tra due pattern usando correlazione."""
        # Normalizza entrambi i pattern
        norm1 = self._normalize_prices(pattern1)
        norm2 = self._normalize_prices(pattern2)
        
        # Calcola correlazione e prendi il valore assoluto
        correlation = np.corrcoef(norm1, norm2)[0,1]
        return abs(correlation)
        
    def _calculate_future_correlation(self, data: pd.DataFrame, 
                                   start_idx: int, length: int) -> float:
        """Calcola la correlazione con il pattern successivo."""
        if start_idx + 2*length > len(data):
            return 0
            
        current = data['close'].values[start_idx:start_idx+length]
        future = data['close'].values[start_idx+length:start_idx+2*length]
        
        return self._calculate_similarity(current, future)
        
    def _calculate_pattern_quality(self, similarity: float, 
                                correlation: float, length: int) -> float:
        """Calcola lo score di qualità del pattern."""
        # Normalizza la lunghezza tra 0 e 1
        length_factor = 1 - (length - self.min_pattern_length) / (
            self.max_pattern_length - self.min_pattern_length)
            
        # Pesi per ciascun fattore
        similarity_weight = 0.4
        correlation_weight = 0.4
        length_weight = 0.2
        
        # Calcola score pesato
        quality = (similarity * similarity_weight + 
                  abs(correlation) * correlation_weight + 
                  length_factor * length_weight)
                  
        return quality
        
    def calculate(self, data: pd.DataFrame) -> np.ndarray:
        """Calcola gli score di pattern recognition."""
        prices = data['close'].values
        n = len(prices)
        scores = np.zeros(n)
        self.patterns = []
        
        # Per ogni possibile lunghezza di pattern
        for length in range(self.min_pattern_length, 
                          min(self.max_pattern_length, n//2)):
            
            # Per ogni possibile punto di inizio
            for i in range(n - length):
                pattern = prices[i:i+length]
                
                # Cerca pattern simili nella serie storica
                for j in range(i + length, n - length):
                    candidate = prices[j:j+length]
                    similarity = self._calculate_similarity(pattern, candidate)
                    
                    if similarity >= self.min_confidence:
                        # Calcola correlazione con pattern futuro
                        correlation = self._calculate_future_correlation(
                            data, i, length)
                            
                        # Calcola qualità pattern
                        quality = self._calculate_pattern_quality(
                            similarity, correlation, length)
                            
                        # Memorizza il pattern
                        self.patterns.append(Pattern(
                            sequence=pattern,
                            start_idx=i,
                            end_idx=i+length,
                            confidence=similarity,
                            correlation=correlation,
                            quality_score=quality
                        ))
                        
                        # Aggiorna scores
                        scores[i:i+length] = max(scores[i:i+length], quality)
                        
        return scores
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera un segnale di trading basato sui pattern identificati."""
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
