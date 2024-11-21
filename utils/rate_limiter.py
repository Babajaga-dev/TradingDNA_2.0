"""
Rate Limiter per TradingDNA 2.0
"""
import time
from typing import Dict, Optional
from collections import deque
from core.exceptions import RateLimitError

class RateLimiter:
    """Gestisce il rate limiting delle richieste"""
    
    def __init__(self, max_requests_per_minute: int, max_orders_per_second: int):
        """
        Inizializza il rate limiter
        
        Args:
            max_requests_per_minute: Massimo numero di richieste al minuto
            max_orders_per_second: Massimo numero di ordini al secondo
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_orders_per_second = max_orders_per_second
        
        # Code per tracciare i timestamp delle richieste
        self.requests_queue = deque(maxlen=max_requests_per_minute)
        self.orders_queue = deque(maxlen=max_orders_per_second)
        
        # Contatori per statistiche
        self._stats = {
            "total_requests": 0,
            "total_orders": 0,
            "rate_limit_hits": 0,
            "last_reset": time.time()
        }
    
    def _clean_queue(self, queue: deque, window: float) -> None:
        """
        Rimuove i timestamp più vecchi della finestra temporale
        
        Args:
            queue: Coda dei timestamp
            window: Finestra temporale in secondi
        """
        if not queue:
            return
            
        current_time = time.time()
        cutoff_time = current_time - window
        
        while queue and queue[0] <= cutoff_time:
            queue.popleft()
    
    def check_rate_limit(self, is_order: bool = False) -> None:
        """
        Verifica se la richiesta rispetta i rate limit
        
        Args:
            is_order: True se la richiesta è un ordine
            
        Raises:
            RateLimitError: Se viene superato il rate limit
        """
        current_time = time.time()
        
        # Pulisci le code
        self._clean_queue(self.requests_queue, 60)  # 1 minuto per richieste
        self._clean_queue(self.orders_queue, 1)     # 1 secondo per ordini
        
        # Verifica limiti
        if len(self.requests_queue) >= self.max_requests_per_minute:
            self._stats["rate_limit_hits"] += 1
            reset_time = self.requests_queue[0] + 60 if self.requests_queue else current_time + 60
            raise RateLimitError(
                "Superato limite richieste al minuto",
                "requests_per_minute",
                reset_time,
                {"current": len(self.requests_queue), "max": self.max_requests_per_minute}
            )
            
        if is_order and len(self.orders_queue) >= self.max_orders_per_second:
            self._stats["rate_limit_hits"] += 1
            reset_time = self.orders_queue[0] + 1 if self.orders_queue else current_time + 1
            raise RateLimitError(
                "Superato limite ordini al secondo",
                "orders_per_second",
                reset_time,
                {"current": len(self.orders_queue), "max": self.max_orders_per_second}
            )
            
        # Aggiorna code e statistiche
        self.requests_queue.append(current_time)
        self._stats["total_requests"] += 1
        
        if is_order:
            self.orders_queue.append(current_time)
            self._stats["total_orders"] += 1
    
    def get_stats(self) -> Dict:
        """
        Recupera le statistiche del rate limiter
        
        Returns:
            Dict: Statistiche di utilizzo
        """
        # Pulisci le code prima di recuperare le statistiche
        self._clean_queue(self.requests_queue, 60)
        self._clean_queue(self.orders_queue, 1)
        
        return {
            **self._stats,
            "current_requests_per_minute": len(self.requests_queue),
            "current_orders_per_second": len(self.orders_queue)
        }
    
    def reset_stats(self) -> None:
        """Resetta le statistiche e le code"""
        self._stats = {
            "total_requests": 0,
            "total_orders": 0,
            "rate_limit_hits": 0,
            "last_reset": time.time()
        }
        self.requests_queue.clear()
        self.orders_queue.clear()
        
    def get_remaining_quota(self) -> Dict:
        """
        Calcola la quota rimanente
        
        Returns:
            Dict: Quota rimanente per tipo di limite
        """
        self._clean_queue(self.requests_queue, 60)
        self._clean_queue(self.orders_queue, 1)
        
        return {
            "requests_per_minute": self.max_requests_per_minute - len(self.requests_queue),
            "orders_per_second": self.max_orders_per_second - len(self.orders_queue)
        }
