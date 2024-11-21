"""Test suite for CLI functionality"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import argparse

# Aggiungo la directory root al path per importare i moduli
sys.path.append(str(Path(__file__).parent.parent))

from main import setup_argparse
from cli.commands import handle_init, handle_config, handle_download, handle_log
from utils.initializer import Initializer

def test_setup_argparse():
    """Test configurazione argparse"""
    parser = setup_argparse()
    assert isinstance(parser, argparse.ArgumentParser)
    
    # Test comando menu
    args = parser.parse_args(['menu'])
    assert args.command == 'menu'
    
    # Test comando init
    args = parser.parse_args(['init'])
    assert args.command == 'init'
    assert not args.force
    
    args = parser.parse_args(['init', '--force'])
    assert args.force
    
    # Test comando config
    args = parser.parse_args(['config', 'show'])
    assert args.command == 'config'
    assert args.action == 'show'
    assert args.file is None
    
    args = parser.parse_args(['config', 'validate', '--file', 'test.yaml'])
    assert args.file == 'test.yaml'
    
    # Test comando download
    args = parser.parse_args(['download', '--pair', 'BTC/USDT'])
    assert args.command == 'download'
    assert args.pair == 'BTC/USDT'
    assert args.timeframe is None  # default value rimosso
    assert not args.progress
    
    args = parser.parse_args(['download', '--pair', 'ETH/USDT', '--timeframe', '4h', '--progress'])
    assert args.timeframe == '4h'
    assert args.progress
    
    # Test comando log
    args = parser.parse_args(['log', 'show'])
    assert args.command == 'log'
    assert args.action == 'show'
    assert args.module is None
    
    args = parser.parse_args(['log', 'test', '--module', 'core'])
    assert args.module == 'core'

@patch('cli.commands.Initializer')  # Updated patch path to match where Initializer is imported
def test_handle_init(mock_initializer_class):
    """Test gestione comando init"""
    # Setup del mock per l'istanza
    mock_instance = MagicMock()
    mock_initializer_class.return_value = mock_instance
    
    # Test inizializzazione normale
    args = MagicMock(force=False)
    handle_init(args)
    mock_initializer_class.assert_called_once_with(force=False)
    mock_instance.initialize.assert_called_once()
    
    # Test inizializzazione forzata
    mock_initializer_class.reset_mock()
    mock_instance.reset_mock()
    args = MagicMock(force=True)
    handle_init(args)
    mock_initializer_class.assert_called_once_with(force=True)
    mock_instance.initialize.assert_called_once()
    
    # Test gestione errori
    mock_instance.initialize.side_effect = Exception("Test error")
    with pytest.raises(SystemExit):
        handle_init(args)

def test_handle_config():
    """Test gestione comando config"""
    # Test azione show
    args = MagicMock(action='show', file=None)
    handle_config(args)
    
    # Test azione validate
    args = MagicMock(action='validate', file='test.yaml')
    handle_config(args)

def test_handle_download():
    """Test gestione comando download"""
    # Test download base
    args = MagicMock(
        pair='BTC/USDT',
        timeframe=None,
        progress=False,
        start=None,
        end=None
    )
    handle_download(args)
    
    # Test download con progress
    args = MagicMock(
        pair='ETH/USDT',
        timeframe='4h',
        progress=True,
        start='2024-01-01',
        end='2024-01-31'
    )
    handle_download(args)

@patch('builtins.input')  # Mock builtins.input since rich.console.Console.input uses it internally
@patch('cli.handlers.log.BaseExchange')  # Mock BaseExchange
@patch('cli.handlers.log.DNADataDownloader')  # Mock DNADataDownloader
def test_handle_log(mock_downloader_class, mock_exchange_class, mock_input):
    """Test gestione comando log"""
    # Setup mocks
    mock_exchange = MagicMock()
    mock_exchange_class.return_value = mock_exchange
    
    mock_downloader = MagicMock()
    mock_downloader_class.return_value = mock_downloader
    
    # Each handle_log call needs:
    # 1. Menu choice ('0' to exit)
    # 2. "Press ENTER to continue" prompt ('')
    mock_input.side_effect = [
        # First handle_log call
        '0', '',
        # Second handle_log call
        '0', '',
        # Third handle_log call
        '0', ''
    ]
    
    # Test azione show
    args = MagicMock(action='show', module=None)
    handle_log(args)
    
    # Test azione test
    args = MagicMock(action='test', module='core')
    handle_log(args)
    
    # Test azione clear
    args = MagicMock(action='clear', module=None)
    handle_log(args)
