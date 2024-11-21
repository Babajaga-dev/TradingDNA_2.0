"""Test unitari per MACDGene.

Questo modulo contiene i test per verificare il corretto funzionamento
del gene MACD (Moving Average Convergence Divergence).
"""
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from core.dna.macd_gene import MACDGene

class TestMACDGene(unittest.TestCase):
    """Test suite per MACDGene."""
    
    def setUp(self) -> None:
        """Setup comune per tutti i test."""
        self.gene = MACDGene()
        
        # Dati di test - trend rialzista
        self.test_data_up = pd.DataFrame({
            'close': [
                10.0, 10.2, 10.4, 10.6, 10.8,
                11.0, 11.2, 11.4, 11.6, 11.8,
                12.0, 12.2, 12.4, 12.6, 12.8,
                13.0, 13.2, 13.4, 13.6, 13.8,
                14.0, 14.2, 14.4, 14.6, 14.8,
                15.0, 15.2, 15.4, 15.6, 15.8
            ]
        })
        
        # Dati di test - trend ribassista
        self.test_data_down = pd.DataFrame({
            'close': [
                10.0, 9.8, 9.6, 9.4, 9.2,
                9.0, 8.8, 8.6, 8.4, 8.2,
                8.0, 7.8, 7.6, 7.4, 7.2,
                7.0, 6.8, 6.6, 6.4, 6.2,
                6.0, 5.8, 5.6, 5.4, 5.2,
                5.0, 4.8, 4.6, 4.4, 4.2
            ]
        })
        
    def test_initialization(self) -> None:
        """Verifica corretta inizializzazione."""
        self.assertEqual(self.gene.name, "macd")
        self.assertEqual(self.gene.fast_period, 12)
        self.assertEqual(self.gene.slow_period, 26)
        self.assertEqual(self.gene.signal_period, 9)
        self.assertEqual(self.gene.signal_threshold, 0.0)
        
    def test_calculate_basic(self) -> None:
        """Verifica calcolo base MACD."""
        result = self.gene.calculate(self.test_data_up)
        
        # Verifica presenza di tutte le componenti
        self.assertIn('macd', result)
        self.assertIn('signal', result)
        self.assertIn('histogram', result)
        
        # Verifica dimensioni output
        self.assertEqual(len(result['macd']), len(self.test_data_up))
        self.assertEqual(len(result['signal']), len(self.test_data_up))
        self.assertEqual(len(result['histogram']), len(self.test_data_up))
        
        # Verifica che l'istogramma sia la differenza tra MACD e signal
        np.testing.assert_array_almost_equal(
            result['histogram'],
            result['macd'] - result['signal']
        )
        
        # Verifica valori finali (usando indici positivi)
        self.assertTrue(np.all(~np.isnan(result['macd'][self.gene.slow_period:])))
        self.assertTrue(np.all(~np.isnan(result['signal'][self.gene.slow_period + self.gene.signal_period:])))
        
    def test_calculate_missing_column(self) -> None:
        """Verifica gestione colonna mancante."""
        invalid_data = pd.DataFrame({'wrong': [1, 2, 3]})
        
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data)
            
    def test_generate_signal_bullish(self) -> None:
        """Verifica segnale rialzista."""
        # Usa i dati rialzisti
        signal = self.gene.generate_signal(self.test_data_up)
        self.assertEqual(signal, 1)
            
    def test_generate_signal_bearish(self) -> None:
        """Verifica segnale ribassista."""
        # Usa i dati ribassisti
        signal = self.gene.generate_signal(self.test_data_down)
        self.assertEqual(signal, -1)
            
    def test_generate_signal_neutral(self) -> None:
        """Verifica segnale neutrale."""
        # Crea dati che generano MACD neutrale
        neutral_data = pd.DataFrame({
            'close': [10.0] * 30  # Prezzi costanti = MACD neutrale
        })
        signal = self.gene.generate_signal(neutral_data)
        self.assertEqual(signal, 0)
            
    def test_generate_signal_error(self) -> None:
        """Verifica gestione errori nel calcolo del segnale."""
        with patch.object(MACDGene, 'calculate') as mock_calc:
            mock_calc.side_effect = Exception("Test error")
            signal = self.gene.generate_signal(self.test_data_up)
            self.assertEqual(signal, 0)
            
    def test_update_metrics(self) -> None:
        """Verifica aggiornamento metriche."""
        test_results = {'win_rate': 0.70, 'profit_factor': 1.8}
        self.gene.update_metrics(test_results)
        
        metrics_dict = self.gene.metrics.to_dict()
        self.assertEqual(metrics_dict['win_rate'], 0.70)
        self.assertEqual(metrics_dict['profit_factor'], 1.8)
        
if __name__ == '__main__':
    unittest.main()
