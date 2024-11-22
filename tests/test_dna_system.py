"""Test suite per il sistema DNA.

Questo modulo contiene i test per:
- Geni individuali (RSI, MACD, Bollinger, Volume)
- Sistema DNA completo
- Ottimizzazione parametri
- Validazione strategia
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from core.dna import DNA, RSIGene, MACDGene, BollingerGene, VolumeGene
from utils.config import load_config

@pytest.fixture
def sample_data():
    """Crea un DataFrame di test con dati OHLCV."""
    # Ridotto il numero di periodi per test più veloci
    dates = pd.date_range(start='2023-01-01', periods=100, freq='h')
    
    # Genera prezzi con trend e volatilità più realistici
    t = np.linspace(0, 4*np.pi, 100)  # Cicli completi di mercato
    trend = 100 + 20 * np.sin(t) + np.cumsum(np.random.normal(0, 0.1, 100))
    volatility = np.abs(np.random.normal(0, 1, 100))
    
    close = trend + volatility
    high = close + np.abs(np.random.normal(0, 1, 100))
    low = close - np.abs(np.random.normal(0, 1, 100))
    open_price = close + np.random.normal(0, 0.5, 100)
    
    # Volume correlato con la volatilità
    volume = 1000 + 4000 * np.abs(np.random.normal(0, 1, 100)) * (1 + volatility/10)
    
    return pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)

@pytest.fixture
def dna_config():
    """Carica la configurazione del DNA."""
    return load_config('dna.yaml')

def test_rsi_gene(sample_data, dna_config):
    """Testa il gene RSI."""
    gene = RSIGene()
    config = dna_config['indicators']['rsi']
    
    # Test calcolo RSI
    rsi = gene.calculate(sample_data)
    assert len(rsi) == len(sample_data)
    assert not np.any(np.isnan(rsi[gene.period:]))
    assert np.all((rsi[gene.period:] >= 0) & (rsi[gene.period:] <= 100))
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Verifica parametri configurati correttamente
    assert gene.period == config['period']
    assert gene.params['overbought'] == config['overbought']
    assert gene.params['oversold'] == config['oversold']
    assert gene.params['signal_threshold'] == config['signal_threshold']

def test_macd_gene(sample_data, dna_config):
    """Testa il gene MACD."""
    gene = MACDGene()
    config = dna_config['indicators']['macd']
    
    # Test calcolo MACD
    macd_line, signal_line, histogram = gene.calculate(sample_data)
    assert len(macd_line) == len(sample_data)
    assert len(signal_line) == len(sample_data)
    assert len(histogram) == len(sample_data)
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Verifica parametri configurati correttamente
    assert gene.params['fast_period'] == config['fast_period']
    assert gene.params['slow_period'] == config['slow_period']
    assert gene.params['signal_period'] == config['signal_period']
    assert gene.params['signal_threshold'] == config['signal_threshold']

def test_bollinger_gene(sample_data, dna_config):
    """Testa il gene Bollinger."""
    gene = BollingerGene()
    config = dna_config['indicators']['bollinger']
    
    # Test calcolo Bollinger Bands
    bands = gene.calculate(sample_data)
    assert len(bands['middle']) == len(sample_data)
    assert not np.any(np.isnan(bands['middle'][gene.params['period']:]))
    assert np.all(bands['upper'][gene.params['period']:] >= bands['middle'][gene.params['period']:])
    assert np.all(bands['middle'][gene.params['period']:] >= bands['lower'][gene.params['period']:])
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Verifica parametri configurati correttamente
    assert gene.params['period'] == config['period']
    assert gene.params['num_std'] == config['num_std']
    assert gene.params['signal_threshold'] == config['signal_threshold']

def test_volume_gene(sample_data, dna_config):
    """Testa il gene Volume."""
    gene = VolumeGene()
    config = dna_config['indicators']['volume']
    
    # Test calcolo indicatori volume
    vwap, volume_ma, obv = gene.calculate(sample_data)
    assert len(vwap) == len(sample_data)
    assert len(volume_ma) == len(sample_data)
    assert len(obv) == len(sample_data)
    assert not np.any(np.isnan(vwap[gene.params['vwap_period']:]))
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Verifica parametri configurati correttamente
    assert gene.params['vwap_period'] == config['vwap_period']
    assert gene.params['volume_ma_period'] == config['volume_ma_period']
    assert gene.params['signal_threshold'] == config['signal_threshold']

def test_dna_system(sample_data, dna_config):
    """Testa il sistema DNA completo."""
    dna = DNA()
    config = dna_config['strategies']['validation']
    signals_config = dna_config['signals']
    
    # Aggiungi geni con segnali forti per test
    class StrongSignalGene:
        def __init__(self, name, signal_value):
            self.name = name
            self._signal = signal_value
            self.metrics = type('Metrics', (), {'calculate_fitness': lambda: 1.0})()
            
        def generate_signal(self, data):
            return self._signal
    
    # Aggiungi geni con segnali forti
    dna.add_gene(StrongSignalGene('strong_buy', 1.0))
    dna.add_gene(StrongSignalGene('strong_buy2', 0.9))
    
    # Test generazione segnale strategia
    start_time = datetime.now()
    signal = dna.get_strategy_signal(sample_data)
    signal_latency = (datetime.now() - start_time).total_seconds() * 1000  # ms
    
    # Verifica segnale
    assert -1 <= signal <= 1
    assert abs(signal) >= signals_config['min_confidence'], f"Segnale {signal} non rispetta confidenza minima {signals_config['min_confidence']}"
    
    # Test validazione strategia
    start_time = datetime.now()
    metrics = dna.validate_strategy(sample_data)
    validation_latency = (datetime.now() - start_time).total_seconds() * 1000  # ms
    
    # Verifica presenza metriche
    required_metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'num_trades']
    for metric in required_metrics:
        assert metric in metrics, f"Metrica {metric} mancante"
    
    # Verifica latenze
    assert signal_latency < 1000, f"Latenza segnale {signal_latency}ms troppo alta"
    assert validation_latency < 5000, f"Latenza validazione {validation_latency}ms troppo alta"
    
    # Verifica persistenza metriche
    assert abs(dna.strategy_metrics.total_return - metrics['total_return']) < 1e-6
    assert abs(dna.strategy_metrics.win_rate - metrics['win_rate']) < 1e-6
    assert abs(dna.strategy_metrics.max_drawdown - metrics['max_drawdown']) < 1e-6

def test_strategy_composition(sample_data):
    """Testa la composizione della strategia."""
    dna = DNA()
    
    # Crea geni con segnali noti
    class MockGene:
        def __init__(self, name, signal):
            self.name = name
            self._signal = signal
            self.metrics = type('Metrics', (), {'calculate_fitness': lambda: 1.0})()
            
        def generate_signal(self, data):
            return self._signal
    
    # Aggiungi geni mock con segnali diversi
    dna.add_gene(MockGene('gene1', 1.0))    # Strong buy
    dna.add_gene(MockGene('gene2', -1.0))   # Strong sell
    dna.add_gene(MockGene('gene3', 0.5))    # Weak buy
    dna.add_gene(MockGene('gene4', 0.0))    # Neutral
    
    # Test che il segnale composito sia una media pesata
    signal = dna.get_strategy_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Il segnale dovrebbe essere vicino a 0 data la distribuzione dei segnali
    assert abs(signal) < 0.5

def test_error_handling():
    """Testa la gestione degli errori."""
    dna = DNA()
    
    # Test aggiunta gene invalido
    with pytest.raises(AttributeError):
        dna.add_gene(None)
    
    # Test rimozione gene inesistente
    dna.remove_gene('non_esistente')  # Non dovrebbe sollevare eccezioni
    
    # Test dati invalidi con colonne mancanti
    invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
    
    with pytest.raises(ValueError):
        dna.get_strategy_signal(invalid_data)
        
    # Test dati invalidi con DataFrame vuoto
    empty_data = pd.DataFrame()
    with pytest.raises(ValueError):
        dna.validate_strategy(empty_data)

if __name__ == '__main__':
    pytest.main([__file__])
