"""Test suite for CLI functionality"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import argparse

# Aggiungo la directory root al path per importare i moduli
sys.path.append(str(Path(__file__).parent.parent))

from main import (
    setup_argparse,
    handle_init,
    handle_config,
    handle_download,
    handle_log
)

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
    args = parser.parse_args(['download', 'BTC/USDT'])
    assert args.command == 'download'
    assert args.pair == 'BTC/USDT'
    assert args.timeframe == '1h'  # default value
    assert not args.progress
    
    args = parser.parse_args(['download', 'ETH/USDT', '--timeframe', '4h', '--progress'])
    assert args.timeframe == '4h'
    assert args.progress
    
    # Test comando log
    args = parser.parse_args(['log', 'show'])
    assert args.command == 'log'
    assert args.action == 'show'
    assert args.module is None
    
    args = parser.parse_args(['log', 'test', '--module', 'core'])
    assert args.module == 'core'

@patch('main.Initializer')
def test_handle_init(mock_initializer):
    """Test gestione comando init"""
    # Test inizializzazione normale
    args = MagicMock(force=False)
    handle_init(args)
    mock_initializer.assert_called_once_with(force=False)
    mock_initializer.return_value.initialize.assert_called_once()
    
    # Test inizializzazione forzata
    mock_initializer.reset_mock()
    args = MagicMock(force=True)
    handle_init(args)
    mock_initializer.assert_called_once_with(force=True)
    
    # Test gestione errori
    mock_initializer.return_value.initialize.side_effect = Exception("Test error")
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
        timeframe='1h',
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

def test_handle_log():
    """Test gestione comando log"""
    # Test azione show
    args = MagicMock(action='show', module=None)
    handle_log(args)
    
    # Test azione test
    args = MagicMock(action='test', module='core')
    handle_log(args)
    
    # Test azione clear
    args = MagicMock(action='clear', module=None)
    handle_log(args)
