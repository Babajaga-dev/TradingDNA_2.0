"""
Exchange Manager per TradingDNA 2.0
Gestisce le connessioni agli exchange tramite ccxt
"""
import time
from typing import Dict, List, Optional, Union, Tuple

from core.error_handler import ErrorHandler
from core.exceptions import InvalidSymbolError, ValidationError
from utils.rate_limiter import RateLimiter

class ExchangeManager(ErrorHandler):
    """Gestisce le connessioni e le operazioni con gli exchange"""
    
    def __init__(self, config_path: str = "config/network.yaml"):
        """
        Inizializza il manager degli exchange
        
        Args:
            config_path: Percorso del file di configurazione
        """
        super().__init__(config_path)
        
        # Inizializza rate limiter
        self.rate_limiter = RateLimiter(
            self.config["exchange"]["rate_limits"]["max_requests_per_minute"],
            self.config["exchange"]["rate_limits"]["max_orders_per_second"]
        )
        
        # Inizializza l'exchange
        self.exchange = self._initialize_exchange()
        
    def check_connection(self) -> Tuple[bool, float]:
        """
        Verifica lo stato della connessione e misura la latenza
        
        Returns:
            Tuple[bool, float]: (stato connessione, latenza in ms)
        """
        try:
            start_time = time.time()
            self.exchange.fetch_time()
            latency = (time.time() - start_time) * 1000  # Converti in ms
            
            self._connection_status["last_latency"] = latency
            self._update_connection_status(True)
            
            self.logger.info(f"Connessione OK - Latenza: {latency:.2f}ms")
            return True, latency
            
        except Exception as e:
            self._update_connection_status(False, str(e))
            self.logger.error(f"Errore verifica connessione: {str(e)}")
            return False, 0

    def reconnect(self) -> bool:
        """
        Tenta una riconnessione all'exchange
        
        Returns:
            bool: True se riconnesso con successo
        """
        try:
            self._connection_status["reconnect_attempts"] += 1
            self.logger.info(f"Tentativo riconnessione #{self._connection_status['reconnect_attempts']}")
            
            # Prova a reinizializzare l'exchange
            self.exchange = self._initialize_exchange()
            if not self.exchange:
                return False
                
            # Verifica la connessione
            connected, _ = self.check_connection()
            return connected
            
        except Exception as e:
            self.logger.error(f"Errore riconnessione: {str(e)}")
            self._update_connection_status(False, str(e))
            return False
                
    def fetch_ohlcv(self, symbol: str, timeframe: str, since: Optional[int] = None, 
                    limit: Optional[int] = None) -> List:
        """
        Recupera i dati OHLCV per un simbolo
        
        Args:
            symbol: Simbolo trading (es. "BTC/USDT")
            timeframe: Timeframe (es. "1m", "1h")
            since: Timestamp Unix ms (opzionale)
            limit: Numero massimo candele (opzionale)
            
        Returns:
            List: Lista di candele OHLCV
        """
        self._validate_symbol_timeframe(symbol, timeframe)
        self.rate_limiter.check_rate_limit()
            
        self.logger.info(f"Recupero OHLCV {symbol} {timeframe}")
        return self._handle_request(
            self.exchange.fetch_ohlcv,
            False,
            symbol,
            timeframe,
            since,
            limit
        )
        
    def fetch_ticker(self, symbol: str) -> Dict:
        """
        Recupera il ticker per un simbolo
        
        Args:
            symbol: Simbolo trading (es. "BTC/USDT")
            
        Returns:
            Dict: Dati ticker
        """
        self._validate_symbol_timeframe(symbol)
        self.rate_limiter.check_rate_limit()
            
        self.logger.info(f"Recupero ticker {symbol}")
        return self._handle_request(
            self.exchange.fetch_ticker,
            False,
            symbol
        )
        
    def fetch_order_book(self, symbol: str, limit: Optional[int] = None) -> Dict:
        """
        Recupera l'order book per un simbolo
        
        Args:
            symbol: Simbolo trading (es. "BTC/USDT")
            limit: Profondità order book (opzionale)
            
        Returns:
            Dict: Order book
        """
        self._validate_symbol_timeframe(symbol)
        self.rate_limiter.check_rate_limit()
            
        self.logger.info(f"Recupero order book {symbol}")
        return self._handle_request(
            self.exchange.fetch_order_book,
            False,
            symbol,
            limit
        )
        
    def _validate_symbol_timeframe(self, symbol: str, timeframe: Optional[str] = None) -> None:
        """
        Valida simbolo e timeframe
        
        Args:
            symbol: Simbolo da validare
            timeframe: Timeframe da validare (opzionale)
            
        Raises:
            InvalidSymbolError: Se il simbolo non è valido
            ValidationError: Se il timeframe non è valido
        """
        # Valida simbolo
        if symbol not in [p["symbol"] for p in self.config["pairs"]]:
            raise InvalidSymbolError(
                f"Simbolo {symbol} non configurato",
                symbol,
                self.config["exchange"]["name"]
            )
            
        # Valida timeframe se specificato
        if timeframe:
            pair_config = next(p for p in self.config["pairs"] if p["symbol"] == symbol)
            if timeframe not in pair_config["timeframes"]:
                raise ValidationError(
                    f"Timeframe {timeframe} non valido per {symbol}",
                    "timeframe",
                    timeframe,
                    {"valid_timeframes": pair_config["timeframes"]}
                )
        
    def get_supported_timeframes(self) -> Dict:
        """
        Recupera i timeframe supportati dall'exchange
        
        Returns:
            Dict: Timeframe supportati
        """
        return self.exchange.timeframes
        
    def get_markets(self) -> List[Dict]:
        """
        Recupera tutti i mercati disponibili
        
        Returns:
            List[Dict]: Lista dei mercati
        """
        self.rate_limiter.check_rate_limit()
        return self._handle_request(self.exchange.load_markets)
