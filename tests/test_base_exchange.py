"""
Test suite per BaseExchange
"""
import os
import pytest
from unittest.mock import patch
import yaml
import ccxt

from core.base_exchange import BaseExchange
from core.exceptions import ConfigurationError, AuthenticationError

@pytest.fixture
def test_config():
    return {
        "exchange": {
            "name": "binance",
            "testnet": True,
            "connection": {
                "timeout": 10000,
                "max_retries": 3,
                "retry_delay": 1000,
            }
        },
        "pairs": [
            {
                "symbol": "BTC/USDT",
                "timeframes": ["1m", "5m", "15m", "1h"]
            }
        ]
    }

def test_load_config(test_config, tmp_path):
    """Verifica il caricamento della configurazione"""
    config_path = tmp_path / "network.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
        
    exchange = BaseExchange(str(config_path))
    assert exchange.config["exchange"]["name"] == test_config["exchange"]["name"]
    assert exchange.config["exchange"]["testnet"] == test_config["exchange"]["testnet"]

def test_invalid_config_missing_key(tmp_path):
    """Verifica errore su config invalida"""
    invalid_config = {
        "exchange": {
            "name": "binance"
        }
        # Manca 'pairs'
    }
    
    config_path = tmp_path / "invalid_network.yaml"
    with open(config_path, "w") as f:
        yaml.dump(invalid_config, f)
        
    with pytest.raises(ConfigurationError) as exc_info:
        BaseExchange(str(config_path))
    assert "pairs" in str(exc_info.value)
    assert exc_info.value.config_key == "pairs"

def test_invalid_exchange_name(test_config, tmp_path):
    """Verifica errore su exchange non supportato"""
    test_config["exchange"]["name"] = "invalid_exchange"
    
    config_path = tmp_path / "network.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
        
    with pytest.raises(ConfigurationError) as exc_info:
        BaseExchange(str(config_path))
    assert "non supportato" in str(exc_info.value)
    assert exc_info.value.config_key == "exchange.name"

@patch.dict(os.environ, {
    "BINANCE_API_KEY": "test_key",
    "BINANCE_API_SECRET": "test_secret"
})
def test_initialize_exchange_with_credentials(test_config, tmp_path):
    """Verifica l'inizializzazione con credenziali"""
    config_path = tmp_path / "network.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
    
    with patch("ccxt.binance") as mock_binance:
        mock_exchange = mock_binance.return_value
        BaseExchange(str(config_path))
        
        mock_binance.assert_called_once()
        call_args = mock_binance.call_args[0][0]
        assert call_args["apiKey"] == "test_key"
        assert call_args["secret"] == "test_secret"
        assert call_args["testnet"] is True

def test_authentication_error(test_config, tmp_path):
    """Verifica errore di autenticazione"""
    config_path = tmp_path / "network.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
        
    with patch("ccxt.binance") as mock_binance:
        mock_binance.side_effect = ccxt.AuthenticationError("Invalid API key")
        
        with pytest.raises(AuthenticationError) as exc_info:
            BaseExchange(str(config_path))
        assert "Invalid API key" in str(exc_info.value)
        assert exc_info.value.exchange == "binance"
