"""Test per il modulo DNADataDownloader."""
import pytest
from core.dna_downloader import DNADataDownloader
from core.exceptions import DNADataError, ConfigurationError
from core.base_exchange import BaseExchange

def test_calculate_candles_for_timeframe():
    """Test del calcolo proporzionale delle candele."""
    downloader = DNADataDownloader(BaseExchange("config/network.yaml"))
    
    # Test calcolo da 1d a timeframe più piccoli
    assert downloader._calculate_candles_for_timeframe("1d", 100, "4h") == 600  # 1d = 6 * 4h
    assert downloader._calculate_candles_for_timeframe("1d", 100, "1h") == 2400  # 1d = 24 * 1h
    assert downloader._calculate_candles_for_timeframe("1d", 100, "15m") == 9600  # 1d = 96 * 15m
    
    # Test calcolo da 4h a timeframe più piccoli
    assert downloader._calculate_candles_for_timeframe("4h", 100, "1h") == 400  # 4h = 4 * 1h
    assert downloader._calculate_candles_for_timeframe("4h", 100, "15m") == 1600  # 4h = 16 * 15m
    
    # Test stesso timeframe
    assert downloader._calculate_candles_for_timeframe("1h", 100, "1h") == 100
    assert downloader._calculate_candles_for_timeframe("4h", 100, "4h") == 100
    assert downloader._calculate_candles_for_timeframe("1d", 100, "1d") == 100

def test_calculate_candles_for_timeframe_errors():
    """Test gestione errori nel calcolo delle candele."""
    downloader = DNADataDownloader(BaseExchange("config/network.yaml"))
    
    # Test timeframe non supportato
    with pytest.raises(DNADataError):
        downloader._calculate_candles_for_timeframe("invalid", 100, "1h")
    
    with pytest.raises(DNADataError):
        downloader._calculate_candles_for_timeframe("1h", 100, "invalid")

def test_calculate_days_from_candles():
    """Test del calcolo dei giorni dalle candele."""
    downloader = DNADataDownloader(BaseExchange("config/network.yaml"))
    
    # Test calcolo giorni per vari timeframe
    assert downloader._calculate_days_from_candles("1d", 100) == 100.0
    assert downloader._calculate_days_from_candles("4h", 100) == 16.666666666666668  # 100 * 4h = 400h = 16.67d
    assert downloader._calculate_days_from_candles("1h", 100) == 4.166666666666667  # 100 * 1h = 100h = 4.17d
    assert downloader._calculate_days_from_candles("15m", 100) == 1.0416666666666667  # 100 * 15m = 1500m = 1.04d
    
    # Test con zero candele
    assert downloader._calculate_days_from_candles("1d", 0) == 0.0
    
    # Test con numeri grandi
    assert downloader._calculate_days_from_candles("1h", 1000) == 41.666666666666664  # 1000h = 41.67d

def test_calculate_days_from_candles_errors():
    """Test gestione errori nel calcolo dei giorni."""
    downloader = DNADataDownloader(BaseExchange("config/network.yaml"))
    
    # Test timeframe non supportato
    with pytest.raises(DNADataError):
        downloader._calculate_days_from_candles("invalid", 100)

def test_download_candles_timeframe_adaptation():
    """Test dell'adattamento del numero di candele per timeframe."""
    downloader = DNADataDownloader(BaseExchange("config/network.yaml"))
    
    # Mock della funzione fetch_ohlcv per evitare chiamate reali all'exchange
    def mock_fetch_ohlcv(symbol, timeframe, limit):
        return [(i, 100, 101, 99, 100, 1000) for i in range(limit)]
    
    downloader.exchange.fetch_ohlcv = mock_fetch_ohlcv
    
    # Test download con multipli timeframe
    data = downloader.download_candles(
        symbol="BTC/USDT",
        timeframes=["1d", "4h", "1h"],
        num_candles=100
    )
    
    # Verifica che il numero di candele sia stato adattato per ogni timeframe
    assert len(data["1d"]) == 100  # Timeframe di riferimento
    assert len(data["4h"]) == 600  # 6 volte più candele
    assert len(data["1h"]) == 2400  # 24 volte più candele
