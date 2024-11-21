"""Test suite per Pattern Recognition System."""
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from core.dna.pattern_recognition import PatternRecognition, Pattern

class TestPatternRecognition(unittest.TestCase):
    """Test cases per il sistema di pattern recognition."""
    
    def setUp(self):
        """Setup per i test."""
        self.pattern_recognition = PatternRecognition()
        
        # Crea dati di test
        dates = [datetime.now() + timedelta(days=x) for x in range(100)]
        self.test_data = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
    def test_initialization(self):
        """Testa corretta inizializzazione."""
        self.assertIsInstance(self.pattern_recognition, PatternRecognition)
        self.assertEqual(self.pattern_recognition.name, 'pattern_recognition')
        self.assertGreater(self.pattern_recognition.min_pattern_length, 0)
        self.assertGreater(self.pattern_recognition.max_pattern_length, 
                          self.pattern_recognition.min_pattern_length)
        
    def test_normalize_prices(self):
        """Testa normalizzazione prezzi."""
        prices = np.array([100, 101, 99, 102, 98])
        normalized = self.pattern_recognition._normalize_prices(prices)
        
        self.assertAlmostEqual(np.mean(normalized), 0, places=7)
        self.assertAlmostEqual(np.std(normalized), 1, places=7)
        
    def test_calculate_similarity(self):
        """Testa calcolo similarità pattern."""
        pattern1 = np.array([1, 2, 3, 4, 5])
        pattern2 = np.array([2, 3, 4, 5, 6])
        
        similarity = self.pattern_recognition._calculate_similarity(pattern1, pattern2)
        self.assertGreaterEqual(similarity, 0)
        self.assertLessEqual(similarity, 1)
        
    def test_calculate_pattern_quality(self):
        """Testa calcolo qualità pattern."""
        quality = self.pattern_recognition._calculate_pattern_quality(
            similarity=0.8,
            correlation=0.6,
            length=10
        )
        
        self.assertGreaterEqual(quality, 0)
        self.assertLessEqual(quality, 1)
        
    def test_calculate_with_short_data(self):
        """Testa gestione dati insufficienti."""
        short_data = self.test_data.iloc[:3]
        result = self.pattern_recognition.calculate(short_data)
        
        self.assertEqual(len(result), len(short_data))
        self.assertTrue(np.all(result == 0))
        
    def test_calculate_pattern_scores(self):
        """Testa calcolo scores pattern."""
        scores = self.pattern_recognition.calculate(self.test_data)
        
        self.assertEqual(len(scores), len(self.test_data))
        self.assertTrue(np.all(scores >= 0))
        self.assertTrue(np.all(scores <= 1))
        
    def test_generate_signal(self):
        """Testa generazione segnali."""
        signal = self.pattern_recognition.generate_signal(self.test_data)
        
        self.assertGreaterEqual(signal, -1)
        self.assertLessEqual(signal, 1)
        
    def test_pattern_storage(self):
        """Testa memorizzazione pattern."""
        self.pattern_recognition.calculate(self.test_data)
        
        if self.pattern_recognition.patterns:
            pattern = self.pattern_recognition.patterns[0]
            self.assertIsInstance(pattern, Pattern)
            self.assertTrue(hasattr(pattern, 'sequence'))
            self.assertTrue(hasattr(pattern, 'confidence'))
            self.assertTrue(hasattr(pattern, 'quality_score'))
            
    def test_future_correlation(self):
        """Testa calcolo correlazione futura."""
        correlation = self.pattern_recognition._calculate_future_correlation(
            self.test_data, 
            start_idx=50,
            length=10
        )
        
        self.assertGreaterEqual(correlation, -1)
        self.assertLessEqual(correlation, 1)

if __name__ == '__main__':
    unittest.main()
