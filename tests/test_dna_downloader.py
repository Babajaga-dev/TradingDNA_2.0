"""Test per il modulo DNA Downloader."""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from pathlib import Path

from core.dna_downloader import DNADataDownloader, DatasetConfig, DNADataError
from core.base_exchange import BaseExchange
from utils.config import ConfigError

@pytest.fixture
def mock_exchange():
    """Fixture per mock dell'exchange."""
    mock = Mock()
    
    # Mock dei dati OHLCV
    sample_data = [
        # timestamp, open, high, low, close, volume
        [1609459200000, 100.0, 105.0, 95.0, 102.0, 1000.0],
        [1609462800000, 102.0, 107.0, 97.0, 104.0, 1100.0],
        [1609466400000, 104.0, 109.0, 99.0, 106.0, 1200.0]
    ]
    
    # Configura il mock per avere il metodo fetch_ohlcv
    mock.fetch_ohlcv = Mock(return_value=sample_data)
    
    return mock

@pytest.fixture
def downloader(mock_exchange):
    """Fixture per il downloader."""
    with patch('utils.config.load_config') as mock_config:
        # Mock della configurazione
        mock_config.return_value = {
            "data": {
                "base_path": "test_data",
                "split_ratios": {
                    "training": 0.7,
                    "validation": 0.15,
                    "testing": 0.15
                }
            }
        }
        return DNADataDownloader(mock_exchange)

def test_dataset_config_validation():
    """Test validazione configurazione dataset."""
    # Test configurazione valida
    config = DatasetConfig(0.7, 0.15, 0.15)
    assert config.training_ratio == 0.7
    
    # Test configurazione non valida
    with pytest.raises(DNADataError):
        DatasetConfig(0.8, 0.15, 0.15)  # Somma > 1

def test_download_candles(downloader, mock_exchange):
    """Test download candele."""
    # Test download singolo timeframe
    data = downloader.download_candles("BTC/USDT", ["1h"], 3)
    
    assert "1h" in data
    assert isinstance(data["1h"], pd.DataFrame)
    assert len(data["1h"]) == 3
    assert list(data["1h"].columns) == ['open', 'high', 'low', 'close', 'volume']
    
    # Verifica chiamata exchange
    mock_exchange.fetch_ohlcv.assert_called_once_with(
        symbol="BTC/USDT",
        timeframe="1h",
        limit=3
    )
    
    # Test errore download
    mock_exchange.fetch_ohlcv.side_effect = Exception("API error")
    with pytest.raises(DNADataError):
        downloader.download_candles("BTC/USDT", ["1h"], 3)

def test_validate_data(downloader):
    """Test validazione dati."""
    # Dataset valido
    valid_data = {
        "1h": pd.DataFrame({
            'open': [100.0, 102.0],
            'high': [105.0, 107.0],
            'low': [95.0, 97.0],
            'close': [102.0, 104.0],
            'volume': [1000.0, 1100.0]
        }, index=pd.date_range('2021-01-01', periods=2, freq='h'))
    }
    
    downloader.validate_data(valid_data)  # Non dovrebbe sollevare eccezioni
    
    # Test dati mancanti
    invalid_data = {
        "1h": pd.DataFrame({
            'open': [100.0, None],
            'high': [105.0, 107.0],
            'low': [95.0, 97.0],
            'close': [102.0, 104.0],
            'volume': [1000.0, 1100.0]
        }, index=pd.date_range('2021-01-01', periods=2, freq='h'))
    }
    
    with pytest.raises(DNADataError):
        downloader.validate_data(invalid_data)
        
    # Test colonne mancanti
    invalid_data = {
        "1h": pd.DataFrame({
            'open': [100.0, 102.0],
            'close': [102.0, 104.0],
        }, index=pd.date_range('2021-01-01', periods=2, freq='h'))
    }
    
    with pytest.raises(DNADataError):
        downloader.validate_data(invalid_data)

def test_split_data(downloader):
    """Test split dei dati."""
    # Crea dataset di test
    data = {
        "1h": pd.DataFrame({
            'open': range(100),
            'high': range(100),
            'low': range(100),
            'close': range(100),
            'volume': range(100)
        }, index=pd.date_range('2021-01-01', periods=100, freq='h'))
    }
    
    # Split dei dati
    training, validation, testing = downloader.split_data(data)
    
    # Verifica dimensioni split
    assert len(training["1h"]) == 70  # 70% training
    assert len(validation["1h"]) == 15  # 15% validation
    assert len(testing["1h"]) == 15  # 15% testing
    
    # Verifica che gli indici siano continui
    assert training["1h"].index[-1] < validation["1h"].index[0]
    assert validation["1h"].index[-1] < testing["1h"].index[0]

@patch('pandas.DataFrame.to_parquet')
def test_save_data(mock_to_parquet, downloader, tmp_path):
    """Test salvataggio dati."""
    # Crea dataset di test
    data = {
        "1h": pd.DataFrame({
            'open': range(10),
            'high': range(10),
            'low': range(10),
            'close': range(10),
            'volume': range(10)
        }, index=pd.date_range('2021-01-01', periods=10, freq='h'))
    }
    
    # Split dei dati
    training, validation, testing = downloader.split_data(data)
    
    # Test salvataggio
    downloader.save_data(training, validation, testing, "BTC/USDT")
    
    # Verifica chiamate to_parquet
    assert mock_to_parquet.call_count == 3  # Un file per ogni split
    
    # Test errore salvataggio
    mock_to_parquet.side_effect = Exception("Storage error")
    with pytest.raises(DNADataError):
        downloader.save_data(training, validation, testing, "BTC/USDT")

def test_integration(downloader, mock_exchange, tmp_path):
    """Test integrazione completo."""
    # Download dati
    data = downloader.download_candles("BTC/USDT", ["1h", "4h"], 100)
    
    # Validazione
    downloader.validate_data(data)
    
    # Split
    training, validation, testing = downloader.split_data(data)
    
    # Salvataggio
    with patch('pandas.DataFrame.to_parquet') as mock_save:
        downloader.save_data(training, validation, testing, "BTC/USDT")
        assert mock_save.call_count == 6  # 2 timeframes * 3 splits
