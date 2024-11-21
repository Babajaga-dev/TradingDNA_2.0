"""
Custom exceptions per TradingDNA 2.0
"""
from typing import Optional, Dict, Any

class TradingDNAError(Exception):
    """Classe base per le eccezioni di TradingDNA"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class NetworkError(TradingDNAError):
    """Errore di rete con dettagli aggiuntivi"""
    def __init__(self, message: str, retry_count: int = 0, 
                 last_retry_delay: float = 0, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.retry_count = retry_count
        self.last_retry_delay = last_retry_delay

class RateLimitError(TradingDNAError):
    """Errore di rate limiting con informazioni sul limite"""
    def __init__(self, message: str, limit_type: str, 
                 reset_time: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.limit_type = limit_type
        self.reset_time = reset_time

class ExchangeError(TradingDNAError):
    """Errore specifico dell'exchange"""
    def __init__(self, message: str, exchange: str, 
                 error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.exchange = exchange
        self.error_code = error_code

class ValidationError(TradingDNAError):
    """Errore di validazione parametri"""
    def __init__(self, message: str, param: str, 
                 value: Any, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.param = param
        self.value = value

class ConfigurationError(TradingDNAError):
    """Errore di configurazione"""
    def __init__(self, message: str, config_key: str, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.config_key = config_key

class AuthenticationError(TradingDNAError):
    """Errore di autenticazione"""
    def __init__(self, message: str, exchange: str, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.exchange = exchange

class InsufficientFundsError(TradingDNAError):
    """Errore fondi insufficienti"""
    def __init__(self, message: str, symbol: str, 
                 required: float, available: float, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.symbol = symbol
        self.required = required
        self.available = available

class InvalidSymbolError(TradingDNAError):
    """Errore simbolo non valido"""
    def __init__(self, message: str, symbol: str, 
                 exchange: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.symbol = symbol
        self.exchange = exchange
