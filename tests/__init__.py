"""
Test suite per TradingDNA 2.0
Include:
- Test unitari
- Test di integrazione
- Fixtures condivise
- Utility per il testing
"""

from pathlib import Path

# Definizione percorsi importanti
TESTS_DIR = Path(__file__).parent
PROJECT_ROOT = TESTS_DIR.parent

# Configurazione test
TEST_CONFIG_DIR = TESTS_DIR / "test_config"
TEST_DATA_DIR = TESTS_DIR / "test_data"

# Costanti per il testing
TEST_PAIRS = ["BTC/USDT", "ETH/USDT"]
TEST_TIMEFRAMES = ["1m", "5m", "1h"]
TEST_INITIAL_CAPITAL = 10000

def get_test_config_path(filename: str) -> Path:
    """Returns the path to a test configuration file"""
    return TEST_CONFIG_DIR / filename

def get_test_data_path(filename: str) -> Path:
    """Returns the path to a test data file"""
    return TEST_DATA_DIR / filename
