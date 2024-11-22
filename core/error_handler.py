"""
Gestore errori per exchange
"""
import time
import random
from typing import Dict, Optional, Union, List, Any, Callable
import ccxt
from ccxt import NetworkError, RateLimitExceeded, ExchangeError, InsufficientFunds, BadSymbol

from core.base_exchange import BaseExchange
from core.exceptions import (
    NetworkError as DNANetworkError,
    RateLimitError, ExchangeError as DNAExchangeError,
    InsufficientFundsError, InvalidSymbolError, TradingDNAError
)
from utils.logger_base import get_component_logger

logger = get_component_logger("error_handler")

class ErrorHandler(BaseExchange):
    """Gestisce gli errori delle richieste all'exchange"""
    
    def __init__(self, config_path: str):
        """
        Inizializza l'error handler
        
        Args:
            config_path: Percorso del file di configurazione
        """
        super().__init__(config_path)
        self._connection_status = {
            "connected": False,
            "last_latency": None,
            "errors_count": 0,
            "last_error": None,
            "reconnect_attempts": 0
        }
        
    def _calculate_backoff_delay(self, attempt: int, base_delay: float) -> float:
        """
        Calcola il delay per il backoff esponenziale
        
        Args:
            attempt: Numero del tentativo corrente
            base_delay: Delay base in millisecondi
            
        Returns:
            float: Delay calcolato in secondi
        """
        # Converti base_delay da ms a secondi
        base_delay_seconds = base_delay / 1000
        
        # Calcola delay con jitter
        max_delay = base_delay_seconds * (2 ** attempt)
        jitter = random.uniform(0, 0.1 * max_delay)  # 10% jitter
        delay = min(max_delay + jitter, 30)  # Max 30 secondi
        
        return delay
            
    def _handle_request(self, func: Callable, is_order: bool = False, 
                       *args, **kwargs) -> Optional[Union[Dict, List]]:
        """
        Gestisce le richieste all'exchange con retry e backoff
        
        Args:
            func: Funzione da eseguire
            is_order: True se la richiesta è un ordine
            *args: Argomenti posizionali
            **kwargs: Argomenti nominali
            
        Returns:
            Optional[Union[Dict, List]]: Risultato della richiesta
            
        Raises:
            NetworkError: Per errori di rete
            RateLimitError: Per errori di rate limiting
            ExchangeError: Per altri errori dell'exchange
        """
        max_retries = self.config["exchange"]["connection"]["max_retries"]
        base_delay = self.config["exchange"]["connection"]["retry_delay"]
        
        for attempt in range(max_retries):
            try:
                # Esegui richiesta
                result = func(*args, **kwargs)
                self._update_connection_status(True)
                return result
                
            except RateLimitExceeded as e:
                self._update_connection_status(False, str(e))
                raise RateLimitError(
                    f"Rate limit superato: {str(e)}",
                    "exchange",
                    time.time() + 60,  # Reset dopo 1 minuto
                    {"error": str(e)}
                )
                
            except NetworkError as e:
                delay = self._calculate_backoff_delay(attempt, base_delay)
                self._update_connection_status(False, str(e))
                
                if attempt == max_retries - 1:
                    raise DNANetworkError(
                        f"Errore rete dopo {max_retries} tentativi: {str(e)}",
                        attempt,
                        delay,
                        {"last_error": str(e)}
                    )
                    
                self.logger.warning(
                    f"Tentativo {attempt + 1}/{max_retries} fallito: {str(e)}. "
                    f"Retry tra {delay:.1f}s"
                )
                time.sleep(delay)
                
            except InsufficientFunds as e:
                self._update_connection_status(False, str(e))
                raise InsufficientFundsError(
                    f"Fondi insufficienti: {str(e)}",
                    kwargs.get("symbol", "unknown"),
                    0,  # Required amount not available from ccxt
                    0,  # Available amount not available from ccxt
                    {"error": str(e)}
                )
                
            except BadSymbol as e:
                self._update_connection_status(False, str(e))
                raise InvalidSymbolError(
                    f"Simbolo non valido: {str(e)}",
                    kwargs.get("symbol", "unknown"),
                    self.config["exchange"]["name"],
                    {"error": str(e)}
                )
                
            except ExchangeError as e:
                self._update_connection_status(False, str(e))
                raise DNAExchangeError(
                    f"Errore exchange: {str(e)}",
                    self.config["exchange"]["name"],
                    getattr(e, "code", None),
                    {"error": str(e)}
                )
                
            except Exception as e:
                self._update_connection_status(False, str(e))
                self.logger.error(f"Errore inaspettato: {str(e)}")
                raise TradingDNAError(
                    f"Errore inaspettato: {str(e)}",
                    {"error": str(e)}
                )
                
    def _update_connection_status(self, connected: bool, error: str = None) -> None:
        """
        Aggiorna lo stato della connessione
        
        Args:
            connected: True se connesso, False altrimenti
            error: Messaggio di errore opzionale
        """
        self._connection_status["connected"] = connected
        if not connected:
            self._connection_status["errors_count"] += 1
            self._connection_status["last_error"] = error
        else:
            self._connection_status["errors_count"] = 0
            self._connection_status["last_error"] = None
            
    def get_connection_status(self) -> Dict:
        """
        Recupera lo stato della connessione
        
        Returns:
            Dict: Stato della connessione
        """
        return self._connection_status.copy()
