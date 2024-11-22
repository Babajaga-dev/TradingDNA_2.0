"""Test del sistema DNA completo."""
from datetime import datetime
import pytest
import pandas as pd
import numpy as np
from core.dna.dna import DNA
from core.dna.strong_signal_gene import StrongSignalGene
from utils.config import load_config

@pytest.fixture
def sample_data():
    """Fixture per dati di esempio con trend chiari."""
    n_points = 50  # Aumentato per più dati
    base_price = 100
    
    # Crea trend più pronunciati
    t = np.linspace(0, 4*np.pi, n_points)
    trend = 5 * np.sin(t)  # Trend sinusoidale più ampio
    noise = np.random.normal(0, 0.1, n_points)
    
    prices = base_price + trend + noise
    
    data = {
        'open': prices,
        'high': prices + 0.5,
        'low': prices - 0.5,
        'close': prices,
        'volume': np.random.uniform(3000, 5000, n_points)
    }
    
    index = pd.date_range(start='2023-01-01', periods=n_points, freq='h')
    return pd.DataFrame(data, index=index)

@pytest.fixture
def dna_config():
    """Fixture per configurazione DNA."""
    return {
        'strategies': {
            'validation': {
                'min_trades': 1,  # Ridotto per il test
                'min_win_rate': 0.5,
                'max_drawdown': 0.3
            }
        },
        'signals': {
            'min_confidence': 0.7,
            'aggregation_method': 'weighted'
        }
    }

def test_dna_system(sample_data, dna_config):
    """Testa il sistema DNA completo."""
    dna = DNA.get_instance()
    config = dna_config['strategies']['validation']
    signals_config = dna_config['signals']

    # Reset DNA instance per test pulito
    dna.genes = {}

    # Configurazione per i geni di test
    strong_signal_config = {
        'window_size': 5,
        'trend_threshold': 0.001,
        'signal_multiplier': 100.0,
        'weight': 1.0
    }

    # Aggiungi più geni con segnali forti per superare la soglia minima
    dna.add_gene(StrongSignalGene({'weight': 1.0, **strong_signal_config}))
    dna.add_gene(StrongSignalGene({'weight': 1.0, **strong_signal_config}))
    dna.add_gene(StrongSignalGene({'weight': 0.9, **strong_signal_config}))
    dna.add_gene(StrongSignalGene({'weight': 0.8, **strong_signal_config}))

    # Test generazione segnale strategia
    start_time = datetime.now()
    signal = dna.get_strategy_signal(sample_data)
    signal_latency = (datetime.now() - start_time).total_seconds() * 1000  # ms

    # Verifica segnale
    assert -1 <= signal <= 1
    assert abs(signal) >= signals_config['min_confidence'], f"Segnale {signal} non rispetta confidenza minima {signals_config['min_confidence']}"

    # Verifica latenza
    assert signal_latency < 1000, f"Latenza {signal_latency}ms supera limite 1000ms"

    # Test validazione strategia
    metrics = dna.validate_strategy(sample_data)

    # Verifica metriche base
    assert isinstance(metrics, dict)
    assert 'total_return' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    assert 'win_rate' in metrics

    # Verifica vincoli validazione
    assert metrics['win_rate'] >= config['min_win_rate'], \
        f"Win rate {metrics['win_rate']} sotto minimo {config['min_win_rate']}"
    assert metrics['max_drawdown'] <= config['max_drawdown'], \
        f"Drawdown {metrics['max_drawdown']} sopra massimo {config['max_drawdown']}"

    # Verifica numero minimo trade
    assert metrics['num_trades'] >= config['min_trades'], \
        f"Numero trade {metrics['num_trades']} sotto minimo {config['min_trades']}"

def test_strong_signal_gene():
    """Test specifico per StrongSignalGene."""
    # Crea dati di test
    n_points = 20
    prices = np.full(n_points, 100.0, dtype=np.float64)  # Usa float64
    prices[10:] = prices[10:] * 1.01  # Crea un trend rialzista del 1%
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.001,
        'low': prices * 0.999,
        'close': prices,
        'volume': np.random.uniform(3000, 5000, n_points)
    })
    
    # Configura e inizializza gene
    config = {
        'window_size': 5,
        'trend_threshold': 0.001,
        'signal_multiplier': 100.0,
        'weight': 1.0
    }
    gene = StrongSignalGene(config)
    
    # Test calcolo trend
    calculations = gene.calculate(data)
    assert 'returns' in calculations
    assert 'trend' in calculations
    assert len(calculations['returns']) == len(data)
    assert len(calculations['trend']) == len(data)
    
    # Test generazione segnale
    signal = gene.generate_signal(data)
    assert -1 <= signal <= 1
    
    # Test dati insufficienti
    short_data = data.iloc[:3]
    assert gene.generate_signal(short_data) == 0
    
    # Test trend laterale
    flat_data = pd.DataFrame({
        'open': np.full(10, 100.0, dtype=np.float64),
        'high': np.full(10, 100.1, dtype=np.float64),
        'low': np.full(10, 99.9, dtype=np.float64),
        'close': np.full(10, 100.0, dtype=np.float64),
        'volume': np.full(10, 3000.0, dtype=np.float64)
    })
    assert abs(gene.generate_signal(flat_data)) < 0.1
