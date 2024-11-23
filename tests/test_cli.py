"""Test module for CLI functionality."""
import pytest
from unittest.mock import MagicMock, patch, call
import pandas as pd
from rich.console import Console
from rich.table import Table

from cli.handlers.dna import DNAMainHandler
from cli.menus.dna import DNAMenu
from utils.initializer import InitializationError

@pytest.fixture
def mock_dna_handler():
    """Create a mock DNAHandler."""
    return MagicMock(spec=DNAMainHandler)

@pytest.fixture
def mock_console():
    """Create a mock Console."""
    console = MagicMock(spec=Console)
    console.input.return_value = "0"  # Default to exit option
    return console

@pytest.fixture
def mock_table():
    """Create a mock Table."""
    table = MagicMock(spec=Table)
    table.add_column = MagicMock()
    table.add_row = MagicMock()
    return table

@pytest.fixture
def mock_dna_menu():
    """Create a mock DNAMenu."""
    menu = DNAMenu()
    menu.handler = MagicMock(spec=DNAMainHandler)
    return menu

def test_dna_menu_display():
    """Test DNA menu display with Rich UI."""
    with patch('cli.menus.dna.Table') as mock_table_class, \
         patch('cli.menus.dna.console') as mock_console:
        # Setup mock table
        mock_table = mock_table_class.return_value
        mock_table.add_column = MagicMock()
        mock_table.add_row = MagicMock()
        
        menu = DNAMenu()
        menu.display_menu()
        
        # Verify console and table usage
        assert mock_console.print.call_count >= 1
        assert mock_table.add_column.call_count >= 1
        assert mock_table.add_row.call_count >= 1

def test_dna_menu_main_options():
    """Test main menu options."""
    with patch('cli.menus.dna.console') as mock_console, \
         patch('cli.menus.dna.show_progress') as mock_progress, \
         patch('cli.menus.dna.time.sleep', return_value=None):
        mock_progress.return_value.__enter__.return_value = MagicMock()
        mock_console.input.return_value = "0"
        
        menu = DNAMenu()
        menu.handler = MagicMock(spec=DNAMainHandler)
        
        # Test initialization
        menu.handle_choice("1")
        menu.handler.handle_init.assert_called_once()
        
        # Test optimization
        menu.handle_choice("3")
        menu.handler.handle_optimization.assert_called_once()
        
        # Test validation
        menu.handle_choice("4")
        menu.handler.handle_validation.assert_called_once()
        
        # Test composition
        menu.handle_choice("5")
        menu.handler.handle_composition.assert_called_once()
        
        # Test pattern analysis
        menu.handle_choice("6")
        menu.handler.handle_pattern_analysis.assert_called_once()
        
        # Test indicators
        menu.handle_choice("7")
        menu.handler.handle_indicators.assert_called_once()
        
        # Test scoring
        menu.handle_choice("8")
        menu.handler.handle_scoring.assert_called_once()
        
        # Test exit
        assert menu.handle_choice("0") is False
        
        # Test invalid choice
        assert menu.handle_choice("9") is True

def test_genes_submenu():
    """Test genes submenu functionality."""
    with patch('cli.menus.dna.console') as mock_console, \
         patch('cli.menus.dna.show_progress') as mock_progress, \
         patch('cli.menus.dna.time.sleep', return_value=None):
        mock_progress.return_value.__enter__.return_value = MagicMock()
        
        # Setup input sequence with enough values for the menu loop
        mock_console.input.side_effect = ["1", "", "0"]  # Select RSI, continue, exit
        
        menu = DNAMenu()
        menu.handler = MagicMock(spec=DNAMainHandler)
        
        # Enter gene management and select RSI
        menu._handle_genes()
        
        # Verify RSI gene handler was called
        menu.handler.handle_gene.assert_called_with('rsi')

def test_error_handling():
    """Test error handling in menu."""
    with patch('cli.menus.dna.console') as mock_console, \
         patch('cli.menus.dna.show_progress') as mock_progress, \
         patch('cli.menus.dna.time.sleep', return_value=None), \
         patch('cli.menus.dna.print_error') as mock_print_error:
        mock_progress.return_value.__enter__.return_value = MagicMock()
        mock_console.input.return_value = ""
        
        menu = DNAMenu()
        menu.handler = MagicMock(spec=DNAMainHandler)
        menu.handler.handle_init.side_effect = Exception("Test error")
        
        menu.handle_choice("1")
        
        # Verify error was printed
        mock_print_error.assert_called_with("Errore: Test error")

@patch('cli.handlers.dna_base.DNA')
@patch('utils.config.ConfigManager.get_config')
@patch('core.dna.gene.load_config')
def test_dna_handler_init(mock_gene_load_config, mock_get_config, mock_dna_class):
    """Test DNA initialization."""
    mock_config = {
        'indicators': {
            'pattern_recognition': {},
            'rsi': {},
            'macd': {},
            'bollinger': {},
            'volume': {}
        },
        'optimization': {
            'pattern_recognition': {},
            'rsi': {},
            'macd': {},
            'bollinger': {},
            'volume': {}
        }
    }
    mock_get_config.return_value = mock_config
    mock_gene_load_config.return_value = mock_config
    mock_dna_instance = MagicMock()
    mock_dna_class.return_value = mock_dna_instance
    
    handler = DNAMainHandler()
    handler.handle_init()
    
    mock_get_config.assert_called_once_with('dna')
    assert mock_dna_instance.add_gene.call_count == 5

@patch('cli.handlers.dna_base.DNAHandler._load_market_data')
def test_dna_handler_load_market_data(mock_load_market_data):
    """Test market data loading."""
    mock_data = pd.DataFrame({'close': [1, 2, 3]})
    mock_load_market_data.return_value = mock_data
    
    handler = DNAMainHandler()
    handler.handle_pattern_analysis()
    
    mock_load_market_data.assert_called_once()

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

@patch('cli.handlers.config.console')
def test_config_command(mock_console):
    """Test config command."""
    from cli.handlers import handle_config
    mock_console.input.return_value = "0"
    
    # Test show config
    args = MagicMock(action='show', file=None)
    handle_config(args)
    
    # Test validate config
    args = MagicMock(action='validate', file=None)
    handle_config(args)

@patch('cli.handlers.download.console')
def test_download_command(mock_console):
    """Test download command."""
    from cli.handlers import handle_download
    mock_console.input.return_value = "0"
    
    args = MagicMock(
        dataset='all',
        pair=None,
        timeframe=None,
        progress=False
    )
    handle_download(args)

@patch('cli.handlers.log.console')
def test_log_command(mock_console):
    """Test log command."""
    from cli.handlers import handle_log
    mock_console.input.return_value = "0"
    
    # Test show logs
    args = MagicMock(action='show', module=None)
    handle_log(args)
    
    # Test clear logs
    args = MagicMock(action='clear', module=None)
    handle_log(args)
    
    # Test test logs
    args = MagicMock(action='test', module=None)
    handle_log(args)
