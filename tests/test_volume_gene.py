"""Test unitari per VolumeGene.

Questo modulo contiene i test per verificare il corretto funzionamento
del gene Volume per l'analisi dei volumi di trading.
"""
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from core.dna.volume_gene import VolumeGene

class TestVolumeGene(unittest.TestCase):
    """Test suite per VolumeGene."""
    
    def setUp(self) -> None:
        """Setup comune per tutti i test."""
        self.gene = VolumeGene()
        
        # Dati di test - volume in aumento con prezzo
        self.test_data_up = pd.DataFrame({
            'close': [
                10.0, 10.2, 10.4, 10.6, 10.8,
                11.0, 11.2, 11.4, 11.6, 11.8,
                12.0, 12.2, 12.4, 12.6, 12.8,
                13.0, 13.2, 13.4, 13.6, 13.8
            ],
            'volume': [
                1000, 1100, 1200, 1300, 1400,
                1500, 1600, 1700, 1800, 1900,
                2000, 2100, 2200, 2300, 2400,
                2500, 2600, 2700, 2800, 2900
            ]
        })
        
        # Dati di test - volume in aumento con prezzo in discesa
        self.test_data_down = pd.DataFrame({
            'close': [
                10.0, 9.8, 9.6, 9.4, 9.2,
                9.0, 8.8, 8.6, 8.4, 8.2,
                8.0, 7.8, 7.6, 7.4, 7.2,
                7.0, 6.8, 6.6, 6.4, 6.2
            ],
            'volume': [
                1000, 1100, 1200, 1300, 1400,
                1500, 1600, 1700, 1800, 1900,
                2000, 2100, 2200, 2300, 2400,
                2500, 2600, 2700, 2800, 2900
            ]
        })
        
    def test_initialization(self) -> None:
        """Verifica corretta inizializzazione."""
        self.assertEqual(self.gene.name, "volume")
        self.assertEqual(self.gene.period, 20)
        self.assertEqual(self.gene.threshold, 1.5)
        self.assertEqual(self.gene.ma_type, "sma")
        
    def test_calculate_sma(self) -> None:
        """Verifica calcolo con SMA."""
        self.gene.ma_type = "sma"
        result = self.gene.calculate(self.test_data_up)
        
        # Verifica presenza di tutte le componenti
        self.assertIn('volume_ma', result)
        self.assertIn('volume_ratio', result)
        
        # Verifica dimensioni output
        self.assertEqual(len(result['volume_ma']), len(self.test_data_up))
        self.assertEqual(len(result['volume_ratio']), len(self.test_data_up))
        
        # Verifica valori finali (usando indici positivi)
        valid_idx = slice(self.gene.period, None)
        self.assertTrue(np.all(~np.isnan(result['volume_ma'][valid_idx])))
        self.assertTrue(np.all(~np.isnan(result['volume_ratio'][valid_idx])))
        self.assertTrue(np.all(result['volume_ratio'][valid_idx] >= 0))
        
    def test_calculate_ema(self) -> None:
        """Verifica calcolo con EMA."""
        self.gene.ma_type = "ema"
        result = self.gene.calculate(self.test_data_up)
        
        # Verifica presenza di tutte le componenti
        self.assertIn('volume_ma', result)
        self.assertIn('volume_ratio', result)
        
        # Verifica dimensioni output
        self.assertEqual(len(result['volume_ma']), len(self.test_data_up))
        self.assertEqual(len(result['volume_ratio']), len(self.test_data_up))
        
        # Verifica valori finali (usando indici positivi)
        valid_idx = slice(self.gene.period, None)
        self.assertTrue(np.all(~np.isnan(result['volume_ma'][valid_idx])))
        self.assertTrue(np.all(~np.isnan(result['volume_ratio'][valid_idx])))
        self.assertTrue(np.all(result['volume_ratio'][valid_idx] >= 0))
        
    def test_calculate_missing_columns(self) -> None:
        """Verifica gestione colonne mancanti."""
        # Test con volume mancante
        invalid_data1 = pd.DataFrame({'close': [1, 2, 3]})
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data1)
            
        # Test con close mancante
        invalid_data2 = pd.DataFrame({'volume': [1, 2, 3]})
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data2)
            
    def test_generate_signal_volume_spike_up(self) -> None:
        """Verifica segnale con volume spike e prezzo in salita."""
        # Modifica l'ultimo volume per creare uno spike
        data = self.test_data_up.copy()
        data.iloc[-1, data.columns.get_loc('volume')] = data['volume'].iloc[-2] * 2
        
        signal = self.gene.generate_signal(data)
        self.assertEqual(signal, 1)
            
    def test_generate_signal_volume_spike_down(self) -> None:
        """Verifica segnale con volume spike e prezzo in discesa."""
        # Modifica l'ultimo volume per creare uno spike
        data = self.test_data_down.copy()
        data.iloc[-1, data.columns.get_loc('volume')] = data['volume'].iloc[-2] * 2
        
        signal = self.gene.generate_signal(data)
        self.assertEqual(signal, -1)
            
    def test_generate_signal_normal_volume(self) -> None:
        """Verifica segnale con volume nella norma."""
        # Usa i dati originali dove il volume non supera la soglia
        signal = self.gene.generate_signal(self.test_data_up)
        self.assertEqual(signal, 0)
            
    def test_generate_signal_error(self) -> None:
        """Verifica gestione errori nel calcolo del segnale."""
        with patch.object(VolumeGene, 'calculate') as mock_calc:
            mock_calc.side_effect = Exception("Test error")
            signal = self.gene.generate_signal(self.test_data_up)
            self.assertEqual(signal, 0)
            
    def test_update_metrics(self) -> None:
        """Verifica aggiornamento metriche."""
        test_results = {'win_rate': 0.68, 'profit_factor': 1.7}
        self.gene.update_metrics(test_results)
        
        metrics_dict = self.gene.metrics.to_dict()
        self.assertEqual(metrics_dict['win_rate'], 0.68)
        self.assertEqual(metrics_dict['profit_factor'], 1.7)
        
if __name__ == '__main__':
    unittest.main()
