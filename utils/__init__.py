"""
Utility condivise per TradingDNA 2.0
Include funzionalità comuni come:
- Logging
- Configurazione
- Validazione
- Database
"""

from pathlib import Path

# Definizione percorsi importanti
UTILS_DIR = Path(__file__).parent
PROJECT_ROOT = UTILS_DIR.parent

# Costanti condivise
DEFAULT_CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_LOGS_DIR = PROJECT_ROOT / "logs"
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"

# Configurazione encoding
DEFAULT_ENCODING = "utf-8"

# Timeframe constants
TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400
}
