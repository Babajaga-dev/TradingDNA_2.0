"""
Test suite per ExchangeManager
"""
import pytest
from unittest.mock import MagicMock, patch
import yaml
import time

from core.nerve_fetch import ExchangeManager
from core.exceptions import ValidationError, InvalidSymbolError, RateLimitError

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
            },
            "rate_limits": {
                "max_requests_per_minute": 1200,
                "max_orders_per_second": 10,
                "max_positions": 50
            }
        },
        "pairs": [
            {
                "symbol": "BTC/USDT",
                "timeframes": ["1m", "5m", "15m", "1h"],
                "min_qty": 0.0001,
                "price_precision": 2,
                "qty_precision": 8
            }
        ]
    }

@pytest.fixture
def exchange_manager(test_config, tmp_path):
    """Crea un ExchangeManager con config temporanea"""
    config_path = tmp_path / "network.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
    
    with patch("ccxt.binance") as mock_binance:
        mock_binance.return_value = MagicMock()
        manager = ExchangeManager(str(config_path))
        return manager

def test_check_connection_success(exchange_manager):
    """Verifica il test di connessione con successo"""
    def mock_fetch_time():
        time.sleep(0.1)  # Simula latenza di 100ms
        return 1000
        
    exchange_manager.exchange.fetch_time = MagicMock(side_effect=mock_fetch_time)
    
    connected, latency = exchange_manager.check_connection()
    assert connected is True
    assert latency > 0
    assert exchange_manager._connection_status["connected"] is True
    assert exchange_manager._connection_status["last_latency"] == latency

def test_reconnect_success(exchange_manager):
    """Verifica la riconnessione con successo"""
    def mock_fetch_time():
        time.sleep(0.1)  # Simula latenza di 100ms
        return 1000
        
    exchange_manager.exchange.fetch_time = MagicMock(side_effect=mock_fetch_time)
    
    success = exchange_manager.reconnect()
    assert success is True
    assert exchange_manager._connection_status["connected"] is True
    assert exchange_manager._connection_status["reconnect_attempts"] == 1

def test_fetch_ohlcv_validation(exchange_manager):
    """Verifica validazione parametri OHLCV"""
    # Test simbolo invalido
    with pytest.raises(InvalidSymbolError) as exc_info:
        exchange_manager.fetch_ohlcv("INVALID/PAIR", "1h")
    assert "non configurato" in str(exc_info.value)
    assert exc_info.value.symbol == "INVALID/PAIR"
    
    # Test timeframe invalido
    with pytest.raises(ValidationError) as exc_info:
        exchange_manager.fetch_ohlcv("BTC/USDT", "1w")
    assert "Timeframe 1w non valido" in str(exc_info.value)
    assert exc_info.value.param == "timeframe"

def test_fetch_ticker_validation(exchange_manager):
    """Verifica validazione parametri ticker"""
    with pytest.raises(InvalidSymbolError) as exc_info:
        exchange_manager.fetch_ticker("INVALID/PAIR")
    assert "non configurato" in str(exc_info.value)
    assert exc_info.value.symbol == "INVALID/PAIR"

def test_fetch_order_book_validation(exchange_manager):
    """Verifica validazione parametri order book"""
    with pytest.raises(InvalidSymbolError) as exc_info:
        exchange_manager.fetch_order_book("INVALID/PAIR")
    assert "non configurato" in str(exc_info.value)
    assert exc_info.value.symbol == "INVALID/PAIR"

def test_rate_limiter_integration(exchange_manager):
    """Verifica integrazione rate limiter"""
    # Imposta un rate limit basso per il test
    exchange_manager.rate_limiter.max_requests_per_minute = 2
    
    # Prima richiesta ok
    exchange_manager.exchange.fetch_ticker.return_value = {"symbol": "BTC/USDT", "last": 50000}
    result1 = exchange_manager.fetch_ticker("BTC/USDT")
    assert result1["last"] == 50000
    
    # Seconda richiesta ok
    result2 = exchange_manager.fetch_ticker("BTC/USDT")
    assert result2["last"] == 50000
    
    # Terza richiesta deve fallire per rate limit
    with pytest.raises(RateLimitError) as exc_info:
        exchange_manager.fetch_ticker("BTC/USDT")
    assert "Superato limite richieste al minuto" in str(exc_info.value)

def test_get_supported_timeframes(exchange_manager):
    """Verifica il recupero dei timeframe supportati"""
    exchange_manager.exchange.timeframes = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "1h": "1h"
    }
    timeframes = exchange_manager.get_supported_timeframes()
    assert timeframes == exchange_manager.exchange.timeframes

def test_get_markets(exchange_manager):
    """Verifica il recupero dei mercati disponibili"""
    mock_markets = {
        "BTC/USDT": {
            "symbol": "BTC/USDT",
            "base": "BTC",
            "quote": "USDT"
        }
    }
    exchange_manager.exchange.load_markets = MagicMock(return_value=mock_markets)
    
    markets = exchange_manager.get_markets()
    assert markets == mock_markets
    exchange_manager.exchange.load_markets.assert_called_once()
