"""Test suite for CLI functionality"""
import pytest
from unittest.mock import patch, MagicMock, call, ANY
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

@patch('cli.handlers.log.console.input', side_effect=['2', '', '3', '', '0'])
@patch('cli.handlers.log.BaseExchange')
@patch('cli.handlers.log.DNADataDownloader')
@patch('cli.handlers.log.logger')
def test_handle_log(mock_logger, mock_downloader_class, mock_exchange_class, mock_input):
    """Test gestione comando log"""
    # Setup mocks
    mock_exchange = MagicMock()
    mock_exchange_class.return_value = mock_exchange
    
    mock_downloader = MagicMock()
    mock_downloader_class.return_value = mock_downloader
    
    # Test menu log
    args = MagicMock(action='show', module=None)
    handle_log(args)
    
    # Verifica che il menu sia stato mostrato e gestito correttamente
    assert mock_input.call_count == 5  # 3 scelte menu (2,3,0) + 2 "premi invio" (l'ultimo non viene eseguito per l'uscita)
    
    # Verifica la sequenza delle chiamate
    calls = mock_input.call_args_list
    assert len(calls) == 5
    
    # Verifica che siano stati loggati i warning attesi
    mock_logger.warning.assert_any_call("Visualizzazione log non ancora implementata")
    mock_logger.warning.assert_any_call("Pulizia log non ancora implementata")

@patch('cli.handlers.dna.DNA')
@patch('cli.handlers.dna.load_market_data')
def test_handle_dna(mock_load_market_data, mock_dna_class):
    """Test gestione comando dna"""
    # Setup mocks
    mock_dna = MagicMock()
    mock_dna_class.return_value = mock_dna
    
    # Mock dei dati
    mock_data = pd.DataFrame({
        'close': np.random.random(100),
        'volume': np.random.random(100) * 1000
    })
    mock_load_market_data.return_value = mock_data
    
    # Test init
    args = MagicMock(action='init')
    handle_dna(args)
    mock_dna_class.assert_called_once()
    
    # Verifica che tutti i geni siano stati aggiunti
    # Usiamo ANY per confrontare solo il tipo dell'oggetto, non l'istanza
    expected_calls = [
        call(ANY),  # PatternRecognition
        call(ANY),  # RSIGene
        call(ANY),  # MACDGene
        call(ANY),  # BollingerGene
        call(ANY)   # VolumeGene
    ]
    mock_dna.add_gene.assert_has_calls(expected_calls, any_order=True)
    assert mock_dna.add_gene.call_count == 5
    
    # Verifica i tipi dei geni aggiunti
    added_genes = [call.args[0] for call in mock_dna.add_gene.call_args_list]
    gene_types = [type(gene) for gene in added_genes]
    assert PatternRecognition in gene_types
    assert RSIGene in gene_types
    assert MACDGene in gene_types
    assert BollingerGene in gene_types
    assert VolumeGene in gene_types
    
    # Test errori
    mock_dna.add_gene.side_effect = Exception("Test error")
    with pytest.raises(SystemExit):
        handle_dna(MagicMock(action='init'))
    
    # Reset mocks for other tests
    mock_dna_class.reset_mock()
    mock_dna = MagicMock()
    mock_dna_class.return_value = mock_dna
    mock_dna.add_gene.side_effect = None
    
    # Test gene analysis
    args = MagicMock(action='gene', type='rsi')
    handle_dna(args)
    mock_load_market_data.assert_called_once()
    
    # Test optimize
    mock_dna_class.reset_mock()
    mock_load_market_data.reset_mock()
    args = MagicMock(action='optimize')
    handle_dna(args)
    mock_load_market_data.assert_called_once()
    
    # Test validate
    mock_dna_class.reset_mock()
    mock_load_market_data.reset_mock()
    args = MagicMock(action='validate')
    handle_dna(args)
    mock_load_market_data.assert_called_once()
    
    # Test compose
    mock_dna_class.reset_mock()
    mock_load_market_data.reset_mock()
    mock_dna.get_strategy_signal.return_value = 0.7  # Mock signal value
    mock_dna.genes = {'test': MagicMock()}
    mock_dna.genes['test'].generate_signal.return_value = 1
    mock_dna.genes['test'].metrics.calculate_fitness.return_value = 0.8
    args = MagicMock(action='compose')
    handle_dna(args)
    mock_load_market_data.assert_called_once()

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
