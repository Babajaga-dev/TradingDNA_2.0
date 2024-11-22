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
        
        # Dati di test - trend rialzista graduale con più punti
        self.test_data_up = pd.DataFrame({
            'close': [
                10.0, 10.0, 10.0, 10.0, 10.0,  # Base stabile
                10.0, 10.0, 10.0, 10.0, 10.0,
                10.0, 10.0, 10.0, 10.0, 10.0,
                10.0, 10.0, 10.0, 10.0, 10.0,
                10.0, 10.0, 10.0, 10.0, 10.0,  # Primi 25 valori stabili
                10.2, 10.4, 10.6, 10.8, 11.0,  # Inizio movimento
                11.3, 11.6, 11.9, 12.2, 12.5,  # Accelerazione
                12.9, 13.3, 13.7, 14.1, 14.5,  # Forte movimento
                15.0, 15.5, 16.0, 16.5, 17.0   # Movimento finale
            ]
        })
        
        # Dati di test - trend ribassista graduale con più punti
        self.test_data_down = pd.DataFrame({
            'close': [
                20.0, 20.0, 20.0, 20.0, 20.0,  # Base stabile
                20.0, 20.0, 20.0, 20.0, 20.0,
                20.0, 20.0, 20.0, 20.0, 20.0,
                20.0, 20.0, 20.0, 20.0, 20.0,
                20.0, 20.0, 20.0, 20.0, 20.0,  # Primi 25 valori stabili
                19.8, 19.6, 19.4, 19.2, 19.0,  # Inizio movimento
                18.7, 18.4, 18.1, 17.8, 17.5,  # Accelerazione
                17.1, 16.7, 16.3, 15.9, 15.5,  # Forte movimento
                15.0, 14.5, 14.0, 13.5, 13.0   # Movimento finale
            ]
        })
        
    def test_initialization(self) -> None:
        """Verifica corretta inizializzazione."""
        self.assertEqual(self.gene.name, "macd")
        self.assertEqual(self.gene.fast_period, 12)
        self.assertEqual(self.gene.slow_period, 26)
        self.assertEqual(self.gene.signal_period, 9)
        self.assertEqual(self.gene.signal_threshold, 0.3)  # Aggiornato al nuovo valore predefinito
        
    def test_calculate_basic(self) -> None:
        """Verifica calcolo base MACD."""
        macd_line, signal_line, histogram = self.gene.calculate(self.test_data_up)
        
        # Verifica che i risultati siano array numpy
        self.assertIsInstance(macd_line, np.ndarray)
        self.assertIsInstance(signal_line, np.ndarray)
        self.assertIsInstance(histogram, np.ndarray)
        
        # Verifica dimensioni output
        self.assertEqual(len(macd_line), len(self.test_data_up))
        self.assertEqual(len(signal_line), len(self.test_data_up))
        self.assertEqual(len(histogram), len(self.test_data_up))
        
        # Verifica che l'istogramma sia la differenza tra MACD e signal
        np.testing.assert_array_almost_equal(
            histogram,
            macd_line - signal_line
        )
        
        # Verifica valori finali (usando indici positivi)
        self.assertTrue(np.all(~np.isnan(macd_line[self.gene.slow_period:])))
        self.assertTrue(np.all(~np.isnan(signal_line[self.gene.slow_period + self.gene.signal_period:])))
        
    def test_calculate_missing_column(self) -> None:
        """Verifica gestione colonna mancante."""
        invalid_data = pd.DataFrame({'wrong': [1, 2, 3]})
        
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data)
            
    def test_generate_signal_bullish(self) -> None:
        """Verifica segnale rialzista."""
        # Usa i dati con trend rialzista graduale
        signal = self.gene.generate_signal(self.test_data_up)
        self.assertEqual(signal, 1)
            
    def test_generate_signal_bearish(self) -> None:
        """Verifica segnale ribassista."""
        # Usa i dati con trend ribassista graduale
        signal = self.gene.generate_signal(self.test_data_down)
        self.assertEqual(signal, -1)
            
    def test_generate_signal_neutral(self) -> None:
        """Verifica segnale neutrale."""
        # Crea dati che generano MACD neutrale
        neutral_data = pd.DataFrame({
            'close': [10.0] * 45  # Prezzi costanti = MACD neutrale
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
