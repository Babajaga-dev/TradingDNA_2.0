"""Test unitari per Pattern Recognition.

Questo modulo contiene i test per verificare il corretto funzionamento
del sistema di riconoscimento pattern.
"""
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from core.dna.pattern_recognition import PatternRecognition, Pattern

class TestPatternRecognition(unittest.TestCase):
    """Test suite per PatternRecognition."""
    
    def setUp(self) -> None:
        """Setup comune per tutti i test."""
        self.gene = PatternRecognition()
        
        # Dati di test - pattern ripetitivo
        self.test_data = pd.DataFrame({
            'close': [
                10.0, 10.2, 10.4, 10.2, 10.0,  # Pattern 1
                10.0, 10.2, 10.4, 10.2, 10.0,  # Pattern 2 (ripetuto)
                10.0, 10.2, 10.4, 10.2, 10.0,  # Pattern 3 (ripetuto)
                10.0, 10.2, 10.4, 10.2, 10.0   # Pattern 4 (ripetuto)
            ]
        })
        
        # Aggiunge colonna rendimenti
        self.test_data['returns'] = self.test_data['close'].pct_change()
        
    def test_initialization(self) -> None:
        """Verifica corretta inizializzazione."""
        self.assertEqual(self.gene.name, "pattern_recognition")
        self.assertEqual(self.gene.min_pattern_length, 5)
        self.assertEqual(self.gene.max_pattern_length, 20)
        self.assertEqual(self.gene.min_confidence, 0.7)
        self.assertEqual(len(self.gene.patterns), 0)
        
    def test_normalize_prices(self) -> None:
        """Verifica normalizzazione prezzi."""
        prices = np.array([10.0, 10.2, 10.4, 10.2, 10.0])
        normalized = self.gene._normalize_prices(prices)
        
        self.assertTrue(np.isclose(np.mean(normalized), 0, atol=1e-10))
        self.assertTrue(np.isclose(np.std(normalized), 1, atol=1e-10))
        
    def test_calculate_similarity(self) -> None:
        """Verifica calcolo similarità tra pattern."""
        pattern1 = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
        pattern2 = np.array([1.0, 2.0, 3.0, 2.0, 1.0])  # Identico
        pattern3 = np.array([3.0, 2.0, 1.0, 2.0, 3.0])  # Inverso
        
        # Pattern identici
        similarity = self.gene._calculate_similarity(pattern1, pattern2)
        self.assertTrue(np.isclose(similarity, 1.0))
        
        # Pattern inversi
        similarity = self.gene._calculate_similarity(pattern1, pattern3)
        self.assertTrue(np.isclose(similarity, 1.0))  # Usa abs(correlation)
        
    def test_calculate_pattern_scores(self) -> None:
        """Verifica calcolo degli score dei pattern."""
        scores = self.gene.calculate(self.test_data)
        
        # Verifica dimensioni output
        self.assertEqual(len(scores), len(self.test_data))
        
        # Verifica che gli score siano nel range [0, 1]
        self.assertTrue(np.all((scores >= 0) & (scores <= 1)))
        
        # Verifica che siano stati trovati pattern
        self.assertTrue(len(self.gene.patterns) > 0)
        
        # Verifica che i pattern trovati abbiano confidence > min_confidence
        self.assertTrue(all(p.confidence >= self.gene.min_confidence 
                          for p in self.gene.patterns))
        
    def test_pattern_storage(self) -> None:
        """Verifica memorizzazione pattern."""
        self.gene.calculate(self.test_data)
        
        # Verifica che ci siano pattern memorizzati
        self.assertTrue(len(self.gene.patterns) > 0)
        
        # Verifica struttura pattern
        for pattern in self.gene.patterns:
            self.assertIsInstance(pattern, Pattern)
            self.assertTrue(isinstance(pattern.sequence, np.ndarray))
            self.assertTrue(isinstance(pattern.start_idx, int))
            self.assertTrue(isinstance(pattern.end_idx, int))
            self.assertTrue(isinstance(pattern.confidence, float))
            self.assertTrue(isinstance(pattern.correlation, float))
            self.assertTrue(isinstance(pattern.quality_score, float))
            
            # Verifica range valori
            self.assertTrue(0 <= pattern.confidence <= 1)
            self.assertTrue(-1 <= pattern.correlation <= 1)
            self.assertTrue(0 <= pattern.quality_score <= 1)
            
    def test_generate_signal(self) -> None:
        """Verifica generazione segnali."""
        signal = self.gene.generate_signal(self.test_data)
        
        # Verifica range segnale
        self.assertTrue(-1 <= signal <= 1)
        
        # Verifica con dati insufficienti
        short_data = pd.DataFrame({
            'close': [10.0, 10.2, 10.4]  # < min_pattern_length
        })
        signal = self.gene.generate_signal(short_data)
        self.assertEqual(signal, 0)
        
        # Verifica con nessun pattern
        self.gene.patterns = []  # Resetta patterns
        signal = self.gene.generate_signal(self.test_data)
        self.assertEqual(signal, 0)
        
    def test_calculate_future_correlation(self) -> None:
        """Verifica calcolo correlazione futura."""
        correlation = self.gene._calculate_future_correlation(
            self.test_data, 
            start_idx=5,  # Dopo il primo pattern
            length=5      # Lunghezza pattern
        )
        
        # Verifica range correlazione
        self.assertTrue(-1 <= correlation <= 1)
        
        # Verifica con indice invalido
        correlation = self.gene._calculate_future_correlation(
            self.test_data,
            start_idx=len(self.test_data),  # Indice oltre i dati
            length=5
        )
        self.assertEqual(correlation, 0)
        
    def test_calculate_pattern_quality(self) -> None:
        """Verifica calcolo qualità pattern."""
        quality = self.gene._calculate_pattern_quality(
            similarity=0.8,
            correlation=0.6,
            length=10
        )
        
        # Verifica range qualità
        self.assertTrue(0 <= quality <= 1)
        
        # Verifica pesi
        # quality = similarity * 0.4 + abs(correlation) * 0.4 + length_factor * 0.2
        expected_length_factor = 1 - (10 - self.gene.min_pattern_length) / (
            self.gene.max_pattern_length - self.gene.min_pattern_length)
        expected_quality = 0.8 * 0.4 + 0.6 * 0.4 + expected_length_factor * 0.2
        
        self.assertTrue(np.isclose(quality, expected_quality))
        
if __name__ == '__main__':
    unittest.main()
