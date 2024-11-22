"""
Classe base per gestione exchange
"""
import os
from typing import Dict, Optional, List, Any
import yaml
import ccxt
from dotenv import load_dotenv

from utils.logger_base import get_component_logger
from core.exceptions import ConfigurationError, AuthenticationError

logger = get_component_logger("exchange")

class BaseExchange:
    """Classe base con funzionalità comuni per gestione exchange"""
    
    def __init__(self, config_path: str):
        """
        Inizializza la classe base
        
        Args:
            config_path: Percorso del file di configurazione
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        self.exchange = self._initialize_exchange()
        
    def _load_config(self, config_path: str) -> Dict:
        """
        Carica la configurazione dal file YAML
        
        Args:
            config_path: Percorso del file di configurazione
            
        Returns:
            Dict: Configurazione caricata
            
        Raises:
            ConfigurationError: Se ci sono errori nel caricamento
        """
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                
            # Valida configurazione minima
            required_keys = ["exchange", "pairs"]
            for key in required_keys:
                if key not in config:
                    raise ConfigurationError(
                        f"Chiave {key} mancante nella configurazione",
                        key
                    )
                    
            # Valida exchange supportato
            exchange_id = config["exchange"]["name"].lower()
            if not hasattr(ccxt, exchange_id):
                raise ConfigurationError(
                    f"Exchange {exchange_id} non supportato",
                    "exchange.name"
                )
                    
            return config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Errore parsing YAML: {str(e)}",
                config_path
            )
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                f"Errore caricamento config: {str(e)}",
                config_path
            )
            
    def _initialize_exchange(self) -> ccxt.Exchange:
        """
        Inizializza la connessione all'exchange
        
        Returns:
            ccxt.Exchange: Istanza dell'exchange inizializzato
            
        Raises:
            ConfigurationError: Se mancano parametri necessari
            AuthenticationError: Se ci sono errori di autenticazione
        """
        try:
            # Carica le variabili d'ambiente
            load_dotenv()
            
            exchange_id = self.config["exchange"]["name"].lower()
            exchange_class = getattr(ccxt, exchange_id)
            
            # Configurazione base
            exchange_config = {
                'enableRateLimit': True,
                'timeout': self.config["exchange"]["connection"]["timeout"],
            }
            
            # Aggiunge API key se presenti nelle variabili d'ambiente
            api_key = os.getenv(f"{exchange_id.upper()}_API_KEY")
            api_secret = os.getenv(f"{exchange_id.upper()}_API_SECRET")
            
            if api_key and api_secret:
                exchange_config.update({
                    'apiKey': api_key,
                    'secret': api_secret
                })
                
            # Usa testnet se configurato
            if self.config["exchange"]["testnet"]:
                if hasattr(exchange_class, 'testnet'):
                    exchange_config['testnet'] = True
                
            exchange = exchange_class(exchange_config)
            self.logger.info(f"Exchange {exchange_id} inizializzato")
            return exchange
            
        except ccxt.AuthenticationError as e:
            raise AuthenticationError(
                f"Errore autenticazione: {str(e)}",
                exchange_id
            )
        except Exception as e:
            self.logger.error(f"Errore inizializzazione exchange: {str(e)}")
            raise
            
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> List[List[Any]]:
        """
        Scarica i dati OHLCV dall'exchange
        
        Args:
            symbol: Simbolo trading (es. BTC/USDT)
            timeframe: Timeframe (es. 1h, 4h, 1d)
            limit: Numero di candele da scaricare
            
        Returns:
            List[List[Any]]: Lista di candele OHLCV
            
        Raises:
            Exception: Se ci sono errori nel download
        """
        try:
            return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as e:
            self.logger.error(f"Errore download OHLCV {symbol} {timeframe}: {str(e)}")
            raise
