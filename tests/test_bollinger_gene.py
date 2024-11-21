"""Test unitari per BollingerGene.

Questo modulo contiene i test per verificare il corretto funzionamento
del gene Bollinger (Bollinger Bands).
"""
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from core.dna.bollinger_gene import BollingerGene

class TestBollingerGene(unittest.TestCase):
    """Test suite per BollingerGene."""
    
    def setUp(self) -> None:
        """Setup comune per tutti i test."""
        self.gene = BollingerGene()
        
        # Dati di test - trend con volatilità crescente
        self.test_data_volatile = pd.DataFrame({
            'close': [
                10.0, 10.1, 10.0, 10.2, 10.1,
                10.3, 10.1, 10.4, 10.2, 10.5,
                10.2, 10.6, 10.3, 10.8, 10.4,
                11.0, 10.5, 11.2, 10.6, 11.4,
                10.7, 11.6, 10.8, 11.8, 10.9,
                12.0, 11.0, 12.2, 11.1, 12.4
            ]
        })
        
        # Dati di test - trend con volatilità bassa
        self.test_data_stable = pd.DataFrame({
            'close': [
                10.0, 10.1, 10.0, 10.1, 10.0,
                10.1, 10.0, 10.1, 10.0, 10.1,
                10.0, 10.1, 10.0, 10.1, 10.0,
                10.1, 10.0, 10.1, 10.0, 10.1,
                10.0, 10.1, 10.0, 10.1, 10.0,
                10.1, 10.0, 10.1, 10.0, 10.1
            ]
        })
        
    def test_initialization(self) -> None:
        """Verifica corretta inizializzazione."""
        self.assertEqual(self.gene.name, "bollinger")
        self.assertEqual(self.gene.period, 20)
        self.assertEqual(self.gene.std_dev, 2.0)
        self.assertEqual(self.gene.signal_threshold, 0.8)
        
    def test_calculate_basic(self) -> None:
        """Verifica calcolo base delle Bollinger Bands."""
        result = self.gene.calculate(self.test_data_volatile)
        
        # Verifica presenza di tutte le componenti
        self.assertIn('middle', result)
        self.assertIn('upper', result)
        self.assertIn('lower', result)
        
        # Verifica dimensioni output
        self.assertEqual(len(result['middle']), len(self.test_data_volatile))
        self.assertEqual(len(result['upper']), len(self.test_data_volatile))
        self.assertEqual(len(result['lower']), len(self.test_data_volatile))
        
        # Verifica valori finali (usando indici positivi)
        valid_idx = slice(self.gene.period, None)  # Indici validi dopo il periodo iniziale
        
        # Verifica che upper sia sempre maggiore di middle
        self.assertTrue(np.all(
            result['upper'][valid_idx] >= result['middle'][valid_idx]
        ))
        
        # Verifica che middle sia sempre maggiore di lower
        self.assertTrue(np.all(
            result['middle'][valid_idx] >= result['lower'][valid_idx]
        ))
        
        # Verifica che i valori non siano NaN dopo il periodo iniziale
        self.assertTrue(np.all(~np.isnan(result['middle'][valid_idx])))
        self.assertTrue(np.all(~np.isnan(result['upper'][valid_idx])))
        self.assertTrue(np.all(~np.isnan(result['lower'][valid_idx])))
        
    def test_calculate_missing_column(self) -> None:
        """Verifica gestione colonna mancante."""
        invalid_data = pd.DataFrame({'wrong': [1, 2, 3]})
        
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data)
            
    def test_generate_signal_lower_band(self) -> None:
        """Verifica segnale quando prezzo tocca banda inferiore."""
        # Crea dati con prezzo vicino alla banda inferiore
        data = self.test_data_volatile.copy()
        bands = self.gene.calculate(data)
        data.iloc[-1, data.columns.get_loc('close')] = bands['lower'][-1] + 0.1
        
        signal = self.gene.generate_signal(data)
        self.assertEqual(signal, 1)
            
    def test_generate_signal_upper_band(self) -> None:
        """Verifica segnale quando prezzo tocca banda superiore."""
        # Crea dati con prezzo vicino alla banda superiore
        data = self.test_data_volatile.copy()
        bands = self.gene.calculate(data)
        data.iloc[-1, data.columns.get_loc('close')] = bands['upper'][-1] - 0.1
        
        signal = self.gene.generate_signal(data)
        self.assertEqual(signal, -1)
            
    def test_generate_signal_middle_band(self) -> None:
        """Verifica segnale quando prezzo è nella banda centrale."""
        # Usa i dati stabili che dovrebbero dare un segnale neutrale
        signal = self.gene.generate_signal(self.test_data_stable)
        self.assertEqual(signal, 0)
            
    def test_generate_signal_zero_bandwidth(self) -> None:
        """Verifica gestione bandwidth zero."""
        # Crea dati con prezzo costante che dovrebbe dare bandwidth zero
        constant_data = pd.DataFrame({
            'close': [10.0] * 30
        })
        signal = self.gene.generate_signal(constant_data)
        self.assertEqual(signal, 0)
            
    def test_generate_signal_error(self) -> None:
        """Verifica gestione errori nel calcolo del segnale."""
        with patch.object(BollingerGene, 'calculate') as mock_calc:
            mock_calc.side_effect = Exception("Test error")
            signal = self.gene.generate_signal(self.test_data_volatile)
            self.assertEqual(signal, 0)
            
    def test_update_metrics(self) -> None:
        """Verifica aggiornamento metriche."""
        test_results = {'win_rate': 0.75, 'profit_factor': 2.0}
        self.gene.update_metrics(test_results)
        
        metrics_dict = self.gene.metrics.to_dict()
        self.assertEqual(metrics_dict['win_rate'], 0.75)
        self.assertEqual(metrics_dict['profit_factor'], 2.0)
        
if __name__ == '__main__':
    unittest.main()
