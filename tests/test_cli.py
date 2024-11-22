"""Test module for CLI functionality."""
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from cli.handlers import DNAHandler
from cli.menus.dna import DNAMenu
from utils.initializer import InitializationError

@pytest.fixture
def mock_dna_handler():
    """Create a mock DNAHandler."""
    return MagicMock(spec=DNAHandler)

@pytest.fixture
def mock_dna_menu():
    """Create a mock DNAMenu."""
    return MagicMock(spec=DNAMenu)

def test_dna_menu(mock_dna_handler):
    """Test DNA menu functionality."""
    menu = DNAMenu()
    menu.handler = mock_dna_handler
    
    # Test menu display
    menu.display_menu()
    
    # Test initialization
    menu.handle_choice("1")
    mock_dna_handler.handle_init.assert_called_once()
    
    # Test gene management
    menu.handle_choice("2")
    
    # Test optimization
    menu.handle_choice("3")
    mock_dna_handler.handle_optimization.assert_called_once()
    
    # Test validation
    menu.handle_choice("4")
    mock_dna_handler.handle_validation.assert_called_once()
    
    # Test composition
    menu.handle_choice("5")
    mock_dna_handler.handle_composition.assert_called_once()
    
    # Test pattern analysis
    menu.handle_choice("6")
    mock_dna_handler.handle_pattern_analysis.assert_called_once()
    
    # Test indicators
    menu.handle_choice("7")
    mock_dna_handler.handle_indicators.assert_called_once()
    
    # Test scoring
    menu.handle_choice("8")
    mock_dna_handler.handle_scoring.assert_called_once()
    
    # Test exit
    assert menu.handle_choice("0") is False
    
    # Test invalid choice
    assert menu.handle_choice("9") is True

def test_dna_handler_initialization():
    """Test DNAHandler initialization."""
    handler = DNAHandler()
    assert handler.dna is not None

@patch('core.dna.DNA')
@patch('cli.handlers.dna.load_config')
def test_dna_handler_init(mock_load_config, mock_dna_class, mock_dna_handler):
    """Test DNA initialization."""
    mock_config = {
        'indicators': {
            'pattern_recognition': {},
            'rsi': {},
            'macd': {},
            'bollinger': {},
            'volume': {}
        }
    }
    mock_load_config.return_value = mock_config
    
    handler = DNAHandler()
    handler.handle_init()
    
    mock_load_config.assert_called_once_with('dna.yaml')
    assert len(mock_dna_class().add_gene.mock_calls) == 5

@patch('cli.handlers.dna.pd.read_parquet')
def test_dna_handler_load_market_data(mock_read_parquet):
    """Test market data loading."""
    mock_data = pd.DataFrame({'close': [1, 2, 3]})
    mock_read_parquet.return_value = mock_data
    
    handler = DNAHandler()
    data = handler._load_market_data()
    
    assert data is mock_data
    mock_read_parquet.assert_called_once()

def test_dna_handler_error_handling(mock_dna_handler):
    """Test error handling in DNAHandler."""
    handler = DNAHandler()
    
    # Test initialization error
    mock_dna_handler.handle_init.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        handler.handle_init()
    
    # Test gene analysis error
    mock_dna_handler.handle_gene.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        handler.handle_gene("rsi")
    
    # Test optimization error
    mock_dna_handler.handle_optimization.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        handler.handle_optimization()
    
    # Test validation error
    mock_dna_handler.handle_validation.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        handler.handle_validation()

def test_init_command():
    """Test init command."""
    from cli.commands import handle_init
    
    # Test successful initialization
    args = MagicMock(force=False)
    assert handle_init(args) is True
    
    # Test initialization error
    with patch('utils.initializer.Initializer.initialize', 
              side_effect=InitializationError("Test error")):
        with pytest.raises(SystemExit):
            handle_init(args)

def test_config_command():
    """Test config command."""
    from cli.handlers import handle_config
    
    # Test show config
    args = MagicMock(action='show', file=None)
    handle_config(args)
    
    # Test validate config
    args = MagicMock(action='validate', file=None)
    handle_config(args)

def test_download_command():
    """Test download command."""
    from cli.handlers import handle_download
    
    args = MagicMock(
        dataset='all',
        pair=None,
        timeframe=None,
        progress=False
    )
    handle_download(args)

def test_log_command():
    """Test log command."""
    from cli.handlers import handle_log
    
    # Test show logs
    args = MagicMock(action='show', module=None)
    handle_log(args)
    
    # Test clear logs
    args = MagicMock(action='clear', module=None)
    handle_log(args)
    
    # Test test logs
    args = MagicMock(action='test', module=None)
    handle_log(args)
