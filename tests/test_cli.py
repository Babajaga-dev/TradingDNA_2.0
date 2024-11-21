"""Test suite for CLI functionality"""
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import sys
import argparse
import pandas as pd
import numpy as np

# Aggiungo la directory root al path per importare i moduli
sys.path.append(str(Path(__file__).parent.parent))

from main import setup_argparse
from cli.commands import (
    handle_init, handle_config, handle_download, 
    handle_log, handle_dna
)
from utils.initializer import Initializer
from core.dna import DNA, RSIGene, MACDGene, BollingerGene, VolumeGene
from core.dna.pattern_recognition import PatternRecognition

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
    assert args.timeframe is None
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
    
    # Test comando dna
    args = parser.parse_args(['dna', 'init'])
    assert args.command == 'dna'
    assert args.action == 'init'
    
    args = parser.parse_args(['dna', 'analyze', '--pair', 'BTC/USDT', '--timeframe', '1h'])
    assert args.pair == 'BTC/USDT'
    assert args.timeframe == '1h'
    
    args = parser.parse_args(['dna', 'indicators'])
    assert args.action == 'indicators'
    
    args = parser.parse_args(['dna', 'score'])
    assert args.action == 'score'

@patch('cli.commands.Initializer')
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

@patch('builtins.input', side_effect=['0', '', '0', '', '0', ''])
@patch('cli.handlers.log.BaseExchange')
@patch('cli.handlers.log.DNADataDownloader')
def test_handle_log(mock_downloader_class, mock_exchange_class, mock_input):
    """Test gestione comando log"""
    # Setup mocks
    mock_exchange = MagicMock()
    mock_exchange_class.return_value = mock_exchange
    
    mock_downloader = MagicMock()
    mock_downloader_class.return_value = mock_downloader
    
    # Test azione show
    args = MagicMock(action='show', module=None)
    handle_log(args)
    
    # Test azione test
    args = MagicMock(action='test', module='core')
    handle_log(args)
    
    # Test azione clear
    args = MagicMock(action='clear', module=None)
    handle_log(args)

@patch('cli.commands.DNA')
@patch('pandas.read_parquet')
def test_handle_dna(mock_read_parquet, mock_dna_class):
    """Test gestione comando dna"""
    # Setup mocks
    mock_dna = MagicMock()
    mock_dna_class.return_value = mock_dna
    
    # Mock dei dati
    mock_data = pd.DataFrame({
        'close': np.random.random(100),
        'volume': np.random.random(100) * 1000
    })
    mock_read_parquet.return_value = mock_data
    
    # Test init
    args = MagicMock(action='init')
    handle_dna(args)
    mock_dna_class.assert_called_once()
    
    # Verifica che tutti i geni siano stati aggiunti
    expected_calls = [
        call(PatternRecognition()),
        call(RSIGene()),
        call(MACDGene()),
        call(BollingerGene()),
        call(VolumeGene())
    ]
    mock_dna.add_gene.assert_has_calls(expected_calls, any_order=True)
    
    # Test analyze
    mock_dna_class.reset_mock()
    args = MagicMock(action='analyze', pair='BTC/USDT', timeframe='1h')
    handle_dna(args)
    mock_read_parquet.assert_called_with(
        Path('data/market/BTC_USDT_1h_training.parquet')
    )
    
    # Test indicators
    mock_dna_class.reset_mock()
    args = MagicMock(action='indicators', pair='BTC/USDT', timeframe='1h')
    handle_dna(args)
    mock_read_parquet.assert_called_with(
        Path('data/market/BTC_USDT_1h_training.parquet')
    )
    
    # Test score
    mock_dna_class.reset_mock()
    args = MagicMock(action='score')
    handle_dna(args)
    
    # Test errori
    mock_dna.add_gene.side_effect = Exception("Test error")
    with pytest.raises(SystemExit):
        handle_dna(MagicMock(action='init'))

@patch('builtins.input', side_effect=['1', '', '0', ''])
def test_dna_submenu(mock_input):
    """Test submenu DNA"""
    from cli.menu import handle_dna_menu
    
    # Mock dei comandi
    mock_commands = {
        'dna': MagicMock()
    }
    
    # Test menu DNA
    handle_dna_menu(mock_commands)
    
    # Verifica chiamata comando
    mock_commands['dna'].assert_called_once()
    args = mock_commands['dna'].call_args[0][0]
    assert args.action == 'init'
