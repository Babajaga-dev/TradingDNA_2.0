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

@pytest.fixture
def sample_data():
    """Crea un DataFrame di test con dati OHLCV."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='h')  # 'h' invece di 'H'
    
    # Genera prezzi con trend e volatilità
    close = np.linspace(100, 120, 100) + np.random.normal(0, 2, 100)
    high = close + np.random.uniform(0, 2, 100)
    low = close - np.random.uniform(0, 2, 100)
    open_price = close - np.random.uniform(-1, 1, 100)
    volume = np.random.uniform(1000, 5000, 100)
    
    return pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)

def test_rsi_gene(sample_data):
    """Testa il gene RSI."""
    gene = RSIGene()
    
    # Test calcolo RSI
    rsi = gene.calculate(sample_data)
    assert len(rsi) == len(sample_data)
    assert np.all((rsi >= 0) & (rsi <= 100))
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Test ottimizzazione
    gene.optimize_params(sample_data)
    assert 5 <= gene.params['period'] <= 30
    assert 60 <= gene.params['overbought'] <= 85
    assert 15 <= gene.params['oversold'] <= 40

def test_macd_gene(sample_data):
    """Testa il gene MACD."""
    gene = MACDGene()
    
    # Test calcolo MACD
    macd_line, signal_line, histogram = gene.calculate(sample_data)
    assert len(macd_line) == len(sample_data)
    assert len(signal_line) == len(sample_data)
    assert len(histogram) == len(sample_data)
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Test ottimizzazione
    gene.optimize_params(sample_data)
    assert 5 <= gene.params['fast_period'] <= 20
    assert 15 <= gene.params['slow_period'] <= 40
    assert 5 <= gene.params['signal_period'] <= 15

def test_bollinger_gene(sample_data):
    """Testa il gene Bollinger."""
    gene = BollingerGene()
    
    # Test calcolo Bollinger Bands
    middle, upper, lower = gene.calculate(sample_data)
    assert len(middle) == len(sample_data)
    assert np.all(upper >= middle)
    assert np.all(middle >= lower)
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Test ottimizzazione
    gene.optimize_params(sample_data)
    assert 10 <= gene.params['period'] <= 30
    assert 1.5 <= gene.params['num_std'] <= 3.0

def test_volume_gene(sample_data):
    """Testa il gene Volume."""
    gene = VolumeGene()
    
    # Test calcolo indicatori volume
    vwap, volume_ma, obv = gene.calculate(sample_data)
    assert len(vwap) == len(sample_data)
    assert len(volume_ma) == len(sample_data)
    assert len(obv) == len(sample_data)
    
    # Test generazione segnali
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Test ottimizzazione
    gene.optimize_params(sample_data)
    assert 5 <= gene.params['vwap_period'] <= 30
    assert 10 <= gene.params['volume_ma_period'] <= 40

def test_dna_system(sample_data):
    """Testa il sistema DNA completo."""
    dna = DNA()
    
    # Aggiungi geni
    dna.add_gene(RSIGene())
    dna.add_gene(MACDGene())
    dna.add_gene(BollingerGene())
    dna.add_gene(VolumeGene())
    
    # Test generazione segnale strategia
    signal = dna.get_strategy_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Test ottimizzazione strategia
    dna.optimize_strategy(sample_data)
    
    # Test validazione strategia
    metrics = dna.validate_strategy(sample_data)
    assert 'total_return' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    assert 'win_rate' in metrics

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
