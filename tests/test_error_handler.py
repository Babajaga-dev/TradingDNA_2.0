"""
Test suite per ErrorHandler
"""
import pytest
import time
from unittest.mock import MagicMock, patch
import ccxt
import yaml

from core.error_handler import ErrorHandler
from core.exceptions import (
    NetworkError, RateLimitError, ExchangeError,
    InsufficientFundsError, InvalidSymbolError
)

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

@pytest.fixture
def mock_exchange():
    """Crea un mock dell'exchange"""
    mock = MagicMock()
    mock.timeframes = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "1h": "1h"
    }
    return mock

@pytest.fixture
def error_handler(test_config, tmp_path, mock_exchange):
    """Crea un ErrorHandler con config temporanea"""
    config_path = tmp_path / "network.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
    
    with patch("ccxt.binance", return_value=mock_exchange):
        handler = ErrorHandler(str(config_path))
        return handler

def test_network_error_with_backoff(error_handler):
    """Verifica backoff esponenziale su errore di rete"""
    error_handler.exchange.fetch_ticker = MagicMock(
        side_effect=[
            ccxt.NetworkError("Test network error"),
            ccxt.NetworkError("Test network error"),
            {"symbol": "BTC/USDT", "last": 50000}
        ]
    )
    
    start_time = time.time()
    result = error_handler._handle_request(
        error_handler.exchange.fetch_ticker,
        False,
        "BTC/USDT"
    )
    elapsed_time = time.time() - start_time
    
    assert result["last"] == 50000
    assert error_handler.exchange.fetch_ticker.call_count == 3
    # Verifica che il tempo totale sia maggiore della somma dei primi due delay
    # (1s + 2s = 3s minimo con backoff)
    assert elapsed_time >= 3

def test_rate_limit_error(error_handler):
    """Verifica errore di rate limit"""
    def raise_rate_limit(*args, **kwargs):
        raise ccxt.RateLimitExceeded("Rate limit exceeded")
    
    mock_func = MagicMock(side_effect=raise_rate_limit)
    
    with pytest.raises(RateLimitError) as exc_info:
        error_handler._handle_request(mock_func, False, "BTC/USDT")
        
    assert "Rate limit superato" in str(exc_info.value)
    assert exc_info.value.limit_type == "exchange"
    assert exc_info.value.reset_time is not None
    assert mock_func.call_count == 1

def test_insufficient_funds_error(error_handler):
    """Verifica errore fondi insufficienti"""
    error_handler.exchange.fetch_ticker = MagicMock(
        side_effect=ccxt.InsufficientFunds("Insufficient funds")
    )
    
    with pytest.raises(InsufficientFundsError) as exc_info:
        error_handler._handle_request(
            error_handler.exchange.fetch_ticker,
            False,
            symbol="BTC/USDT"
        )
    assert "Fondi insufficienti" in str(exc_info.value)
    assert exc_info.value.symbol == "BTC/USDT"

def test_exchange_error_no_retry(error_handler):
    """Verifica che gli errori dell'exchange non causino retry"""
    error_handler.exchange.fetch_ticker = MagicMock(
        side_effect=ccxt.ExchangeError("Test exchange error")
    )
    
    with pytest.raises(ExchangeError) as exc_info:
        error_handler._handle_request(
            error_handler.exchange.fetch_ticker,
            False,
            "BTC/USDT"
        )
    assert "Test exchange error" in str(exc_info.value)
    error_handler.exchange.fetch_ticker.assert_called_once()
    assert error_handler._connection_status["errors_count"] == 1
    assert error_handler._connection_status["connected"] is False

def test_successful_retry_after_network_error(error_handler):
    """Verifica retry con successo dopo errore di rete"""
    error_handler.exchange.fetch_ticker = MagicMock(
        side_effect=[
            ccxt.NetworkError("Test network error"),
            {"symbol": "BTC/USDT", "last": 50000}
        ]
    )
    
    result = error_handler._handle_request(
        error_handler.exchange.fetch_ticker,
        False,
        "BTC/USDT"
    )
    assert result["last"] == 50000
    assert error_handler.exchange.fetch_ticker.call_count == 2
    assert error_handler._connection_status["errors_count"] == 0
    assert error_handler._connection_status["connected"] is True

def test_connection_status_update(error_handler):
    """Verifica aggiornamento stato connessione"""
    # Test errore
    error_handler._update_connection_status(False, "Test error")
    assert error_handler._connection_status["connected"] is False
    assert error_handler._connection_status["errors_count"] == 1
    assert error_handler._connection_status["last_error"] == "Test error"
    
    # Test successo
    error_handler._update_connection_status(True)
    assert error_handler._connection_status["connected"] is True
    assert error_handler._connection_status["errors_count"] == 0
    assert error_handler._connection_status["last_error"] is None

def test_get_connection_status(error_handler):
    """Verifica recupero stato connessione"""
    error_handler._update_connection_status(True)
    status = error_handler.get_connection_status()
    
    assert isinstance(status, dict)
    assert status["connected"] is True
    assert status["errors_count"] == 0
    assert status["last_error"] is None
