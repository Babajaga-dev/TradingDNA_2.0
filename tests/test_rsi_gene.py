"""Test unitari per RSIGene.

Questo modulo contiene i test per verificare il corretto funzionamento
del gene RSI (Relative Strength Index).
"""
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from core.dna.rsi_gene import RSIGene

class TestRSIGene(unittest.TestCase):
    """Test suite per RSIGene."""
    
    def setUp(self) -> None:
        """Setup comune per tutti i test."""
        self.gene = RSIGene()
        
        # Dati di test - trend rialzista più forte per RSI alto
        self.test_data_up = pd.DataFrame({
            'close': [
                10.0, 10.5, 11.0, 11.8, 12.5,
                13.2, 14.0, 15.0, 16.2, 17.5,
                18.8, 20.0, 21.5, 23.0, 24.8,
                26.5, 28.2, 30.0, 32.0, 34.0
            ]
        })
        
        # Dati di test - trend ribassista più forte per RSI basso
        self.test_data_down = pd.DataFrame({
            'close': [
                10.0, 9.5, 9.0, 8.2, 7.5,
                6.8, 6.0, 5.0, 4.2, 3.5,
                2.8, 2.0, 1.5, 1.2, 1.0,
                0.8, 0.6, 0.5, 0.4, 0.3
            ]
        })
        
    def test_initialization(self) -> None:
        """Verifica corretta inizializzazione."""
        self.assertEqual(self.gene.name, "rsi")
        self.assertEqual(self.gene.period, 14)
        self.assertEqual(self.gene.overbought, 70)
        self.assertEqual(self.gene.oversold, 30)
        self.assertEqual(self.gene.signal_threshold, 0.6)
        
    def test_calculate_basic(self) -> None:
        """Verifica calcolo base RSI."""
        rsi = self.gene.calculate(self.test_data_up)
        
        self.assertIsInstance(rsi, np.ndarray)
        self.assertEqual(len(rsi), len(self.test_data_up))
        self.assertTrue(np.all((rsi[self.gene.period:] >= 0) & (rsi[self.gene.period:] <= 100)))
        
    def test_calculate_missing_column(self) -> None:
        """Verifica gestione colonna mancante."""
        invalid_data = pd.DataFrame({'wrong': [1, 2, 3]})
        
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data)
            
    def test_generate_signal_oversold(self) -> None:
        """Verifica segnale in condizione di ipervenduto."""
        # Usa i dati ribassisti che dovrebbero generare RSI basso
        signal = self.gene.generate_signal(self.test_data_down)
        self.assertEqual(signal, 1)
            
    def test_generate_signal_overbought(self) -> None:
        """Verifica segnale in condizione di ipercomprato."""
        # Usa i dati rialzisti che dovrebbero generare RSI alto
        signal = self.gene.generate_signal(self.test_data_up)
        self.assertEqual(signal, -1)
            
    def test_generate_signal_neutral(self) -> None:
        """Verifica segnale in condizione neutrale."""
        # Crea dati che generano RSI neutrale
        neutral_data = pd.DataFrame({
            'close': [10.0] * 20  # Prezzi costanti = RSI neutrale
        })
        signal = self.gene.generate_signal(neutral_data)
        self.assertEqual(signal, 0)
            
    def test_generate_signal_error(self) -> None:
        """Verifica gestione errori nel calcolo del segnale."""
        with patch.object(RSIGene, 'calculate') as mock_calc:
            mock_calc.side_effect = Exception("Test error")
            signal = self.gene.generate_signal(self.test_data_up)
            self.assertEqual(signal, 0)
            
    def test_update_metrics(self) -> None:
        """Verifica aggiornamento metriche."""
        test_results = {'win_rate': 0.65, 'profit_factor': 1.5}
        self.gene.update_metrics(test_results)
        
        metrics_dict = self.gene.metrics.to_dict()
        self.assertEqual(metrics_dict['win_rate'], 0.65)
        self.assertEqual(metrics_dict['profit_factor'], 1.5)
        
if __name__ == '__main__':
    unittest.main()
