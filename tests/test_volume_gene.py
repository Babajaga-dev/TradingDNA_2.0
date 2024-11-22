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
        # Mock della configurazione
        self.config_mock = {
            'indicators': {
                'volume': {
                    'vwap_period': 20,
                    'volume_ma_period': 20,
                    'signal_threshold': 0.1
                }
            }
        }
        
        with patch('core.dna.volume_gene.load_config', return_value=self.config_mock):
            self.gene = VolumeGene()
        
        # Dati di test - trend rialzista
        self.test_data_up = pd.DataFrame({
            'open': [10.0] * 20,
            'high': [11.0] * 20,
            'low': [9.0] * 20,
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
        
        # Dati di test - trend ribassista
        self.test_data_down = pd.DataFrame({
            'open': [10.0] * 20,
            'high': [11.0] * 20,
            'low': [9.0] * 20,
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
        
        # Dati di test - trend laterale per test neutrale
        self.test_data_neutral = pd.DataFrame({
            'open': [10.0] * 20,
            'high': [10.2] * 20,
            'low': [9.8] * 20,
            'close': [10.0] * 20,  # Prezzo costante
            'volume': [1000] * 20  # Volume costante
        })
        
    def test_initialization(self) -> None:
        """Verifica corretta inizializzazione e caricamento config."""
        self.assertEqual(self.gene.name, "volume")
        self.assertEqual(self.gene.params['vwap_period'], 20)
        self.assertEqual(self.gene.params['volume_ma_period'], 20)
        self.assertEqual(self.gene.params['signal_threshold'], 0.1)
        
    def test_calculate(self) -> None:
        """Verifica calcolo indicatori."""
        vwap, volume_ma, obv = self.gene.calculate(self.test_data_up)
        
        # Verifica dimensioni output
        self.assertEqual(len(vwap), len(self.test_data_up))
        self.assertEqual(len(volume_ma), len(self.test_data_up))
        self.assertEqual(len(obv), len(self.test_data_up))
        
        # Verifica valori non-nan
        self.assertTrue(np.all(~np.isnan(vwap)))
        self.assertTrue(np.all(~np.isnan(volume_ma)))
        self.assertTrue(np.all(~np.isnan(obv)))
        
        # Verifica che VWAP sia tra high e low
        high = self.test_data_up['high'].max()
        low = self.test_data_up['low'].min()
        self.assertTrue(np.all(vwap <= high))
        self.assertTrue(np.all(vwap >= low))
        
        # Verifica che Volume MA sia calcolata correttamente
        expected_last_ma = np.mean(self.test_data_up['volume'].iloc[-20:])
        self.assertAlmostEqual(volume_ma[-1], expected_last_ma)
        
        # Verifica OBV crescente con prezzi crescenti
        self.assertTrue(np.all(np.diff(obv) >= 0))
        
    def test_calculate_missing_columns(self) -> None:
        """Verifica gestione colonne mancanti."""
        # Test con volume mancante
        invalid_data1 = pd.DataFrame({
            'open': [1], 'high': [2], 'low': [0], 'close': [1]
        })
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data1)
            
        # Test con close mancante
        invalid_data2 = pd.DataFrame({
            'open': [1], 'high': [2], 'low': [0], 'volume': [100]
        })
        with self.assertRaises(ValueError):
            self.gene.calculate(invalid_data2)
            
    def test_calculate_insufficient_data(self) -> None:
        """Verifica gestione dati insufficienti."""
        short_data = self.test_data_up.iloc[:5]
        with self.assertRaises(ValueError):
            self.gene.calculate(short_data)
            
    def test_generate_signal_volume_spike_up(self) -> None:
        """Verifica segnale con volume alto e prezzo sopra VWAP."""
        # Modifica l'ultimo volume per creare uno spike
        data = self.test_data_up.copy()
        last_volume = data['volume'].iloc[-2]
        data.loc[data.index[-1], 'volume'] = int(last_volume * 3)
        
        signal = self.gene.generate_signal(data)
        self.assertGreater(signal, 0)
        self.assertLessEqual(signal, 1.0)
            
    def test_generate_signal_volume_spike_down(self) -> None:
        """Verifica segnale con volume alto e prezzo sotto VWAP."""
        # Modifica l'ultimo volume per creare uno spike
        data = self.test_data_down.copy()
        last_volume = data['volume'].iloc[-2]
        data.loc[data.index[-1], 'volume'] = int(last_volume * 3)
        
        signal = self.gene.generate_signal(data)
        self.assertLess(signal, 0)
        self.assertGreaterEqual(signal, -1.0)
            
    def test_generate_signal_normal_volume(self) -> None:
        """Verifica segnale con volume nella norma."""
        # Usa i dati neutrali dove prezzo e volume sono costanti
        signal = self.gene.generate_signal(self.test_data_neutral)
        self.assertEqual(signal, 0)
            
    def test_generate_signal_threshold(self) -> None:
        """Verifica applicazione della soglia al segnale."""
        # Test con segnale sotto soglia
        data = self.test_data_up.copy()
        last_volume = data['volume'].iloc[-2]
        data.loc[data.index[-1], 'volume'] = int(last_volume * 1.1)
        
        with patch.dict(self.gene.params, {'signal_threshold': 0.5}):
            signal = self.gene.generate_signal(data)
            self.assertEqual(signal, 0.0)
            
    def test_generate_signal_insufficient_data(self) -> None:
        """Verifica gestione dati insufficienti nel calcolo del segnale."""
        short_data = self.test_data_up.iloc[:5]
        signal = self.gene.generate_signal(short_data)
        self.assertEqual(signal, 0.0)
            
    def test_generate_signal_error(self) -> None:
        """Verifica gestione errori nel calcolo del segnale."""
        with patch.object(VolumeGene, 'calculate') as mock_calc:
            mock_calc.side_effect = Exception("Test error")
            signal = self.gene.generate_signal(self.test_data_up)
            self.assertEqual(signal, 0)
            
    def test_optimize_params(self) -> None:
        """Verifica ottimizzazione parametri."""
        # Mock della configurazione per l'ottimizzazione
        opt_config = {
            'optimization': {
                'volume': {
                    'vwap_period': [5, 30],
                    'volume_ma_period': [10, 40],
                    'signal_threshold': [0.1, 0.5]
                }
            }
        }
        
        original_params = self.gene.params.copy()
        
        with patch('core.dna.volume_gene.load_config', return_value=opt_config):
            self.gene.optimize_params(self.test_data_up)
        
        # Verifica che i parametri siano stati aggiornati
        self.assertNotEqual(self.gene.params, original_params)
        
        # Verifica che i nuovi parametri siano nel range atteso
        self.assertGreaterEqual(self.gene.params['vwap_period'], 5)
        self.assertLessEqual(self.gene.params['vwap_period'], 30)
        self.assertGreaterEqual(self.gene.params['volume_ma_period'], 10)
        self.assertLessEqual(self.gene.params['volume_ma_period'], 40)
        self.assertGreaterEqual(self.gene.params['signal_threshold'], 0.1)
        self.assertLessEqual(self.gene.params['signal_threshold'], 0.5)
        
    def test_logging(self) -> None:
        """Verifica corretta registrazione dei log."""
        with self.assertLogs('VolumeGene', level='INFO') as log:
            # Trigger log durante inizializzazione
            gene = VolumeGene()
            # Trigger log durante generazione segnale
            gene.generate_signal(self.test_data_up)
            
            # Verifica presenza messaggi di log
            self.assertTrue(any('Inizializzato Volume con parametri' in msg for msg in log.output))
            
if __name__ == '__main__':
    unittest.main()
