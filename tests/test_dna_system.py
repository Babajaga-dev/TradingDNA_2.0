"""Test del sistema DNA completo."""
from datetime import datetime
import pytest
import pandas as pd
import numpy as np
from core.dna.dna import DNA
from utils.config import load_config

class GeneMetrics:
    """Classe per le metriche dei geni."""
    def calculate_fitness(self):
        return 1.0

class StrongSignalGene:
    """Gene di test che genera segnali forti costanti."""
    def __init__(self, name, signal_value):
        self.name = name
        self._signal = signal_value
        self.metrics = GeneMetrics()
        self.min_data_points = 5  # Ridotto per testing

    def generate_signal(self, data):
        """Genera un segnale basato sul trend dei dati incrementali."""
        if len(data) < self.min_data_points:
            return 0
            
        # Calcola trend sugli ultimi 5 punti
        window = min(5, len(data))
        recent_data = data.iloc[-window:]
        returns = recent_data['close'].pct_change().fillna(0)
        trend = returns.mean()
        
        # Genera segnale basato sul trend e forza base
        if abs(trend) < 0.001:  # Trend laterale
            return 0
        elif trend > 0:
            return min(abs(trend * 100), 1.0) * self._signal  # Scala il segnale base
        else:
            return -min(abs(trend * 100), 1.0) * self._signal

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

    # Aggiungi più geni con segnali forti per superare la soglia minima
    dna.add_gene(StrongSignalGene('strong_buy1', 1.0))
    dna.add_gene(StrongSignalGene('strong_buy2', 1.0))
    dna.add_gene(StrongSignalGene('strong_buy3', 1.0))
    dna.add_gene(StrongSignalGene('strong_buy4', 0.9))

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
