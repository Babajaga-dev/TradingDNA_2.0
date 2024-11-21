"""
Test suite per RateLimiter
"""
import pytest
import time
from utils.rate_limiter import RateLimiter
from core.exceptions import RateLimitError

def test_init():
    """Verifica inizializzazione"""
    limiter = RateLimiter(60, 2)
    assert limiter.max_requests_per_minute == 60
    assert limiter.max_orders_per_second == 2

def test_check_rate_limit_requests():
    """Verifica rate limit richieste"""
    limiter = RateLimiter(2, 1)  # 2 richieste/min, 1 ordine/sec
    
    # Prima richiesta ok
    limiter.check_rate_limit()
    assert limiter.get_stats()["total_requests"] == 1
    
    # Seconda richiesta ok
    limiter.check_rate_limit()
    assert limiter.get_stats()["total_requests"] == 2
    
    # Terza richiesta deve fallire
    with pytest.raises(RateLimitError) as exc_info:
        limiter.check_rate_limit()
    assert "Superato limite richieste al minuto" in str(exc_info.value)
    assert exc_info.value.limit_type == "requests_per_minute"
    assert limiter.get_stats()["total_requests"] == 2  # Non deve incrementare

def test_check_rate_limit_orders():
    """Verifica rate limit ordini"""
    limiter = RateLimiter(60, 1)  # 60 richieste/min, 1 ordine/sec
    
    # Primo ordine ok
    limiter.check_rate_limit(is_order=True)
    assert limiter.get_stats()["total_orders"] == 1
    
    # Secondo ordine deve fallire
    with pytest.raises(RateLimitError) as exc_info:
        limiter.check_rate_limit(is_order=True)
    assert "Superato limite ordini al secondo" in str(exc_info.value)
    assert exc_info.value.limit_type == "orders_per_second"
    assert limiter.get_stats()["total_orders"] == 1  # Non deve incrementare

def test_rate_limit_reset():
    """Verifica reset rate limit dopo finestra temporale"""
    limiter = RateLimiter(2, 1)  # 2 richieste/min, 1 ordine/sec
    
    # Prima richiesta ok
    limiter.check_rate_limit()
    assert limiter.get_stats()["total_requests"] == 1
    
    # Aspetta reset finestra
    time.sleep(1.1)  # Poco più di 1 secondo
    
    # Seconda richiesta deve essere ok
    limiter.check_rate_limit()
    assert limiter.get_stats()["total_requests"] == 2

def test_get_stats():
    """Verifica statistiche"""
    limiter = RateLimiter(60, 2)
    
    # Esegui alcune richieste
    limiter.check_rate_limit()
    limiter.check_rate_limit(is_order=True)
    
    stats = limiter.get_stats()
    assert stats["total_requests"] == 2
    assert stats["total_orders"] == 1
    assert stats["rate_limit_hits"] == 0

def test_reset_stats():
    """Verifica reset statistiche"""
    limiter = RateLimiter(60, 2)
    
    # Esegui alcune richieste
    limiter.check_rate_limit()
    limiter.check_rate_limit(is_order=True)
    
    # Reset stats
    limiter.reset_stats()
    
    stats = limiter.get_stats()
    assert stats["total_requests"] == 0
    assert stats["total_orders"] == 0
    assert stats["rate_limit_hits"] == 0

def test_get_remaining_quota():
    """Verifica quota rimanente"""
    limiter = RateLimiter(60, 2)
    
    # Stato iniziale
    quota = limiter.get_remaining_quota()
    assert quota["requests_per_minute"] == 60
    assert quota["orders_per_second"] == 2
    
    # Dopo alcune richieste
    limiter.check_rate_limit()
    limiter.check_rate_limit(is_order=True)
    
    quota = limiter.get_remaining_quota()
    assert quota["requests_per_minute"] == 58  # 60 - 2
    assert quota["orders_per_second"] == 1     # 2 - 1

def test_clean_queue():
    """Verifica pulizia code dopo finestra temporale"""
    limiter = RateLimiter(60, 2)
    
    # Esegui richieste
    limiter.check_rate_limit()
    limiter.check_rate_limit(is_order=True)
    
    # Aspetta reset
    time.sleep(1.1)
    
    quota = limiter.get_remaining_quota()
    assert quota["orders_per_second"] == 2  # Reset dopo 1s
    assert quota["requests_per_minute"] == 58  # Due richieste ancora valide
