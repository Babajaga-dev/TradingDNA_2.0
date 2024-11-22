"""Test per il gene Bollinger."""
import pytest
import pandas as pd
import numpy as np
from core.dna.bollinger_gene import BollingerGene

@pytest.fixture
def sample_data():
    """Fixture per dati di esempio."""
    # Crea un dataset stabile per il test
    n_points = 20
    base_price = 100
    prices = np.ones(n_points) * base_price  # Prezzi costanti
    
    data = {
        'open': prices,
        'high': prices + 0.5,
        'low': prices - 0.5,
        'close': prices,
        'volume': np.random.uniform(3000, 5000, n_points)
    }
    
    index = pd.date_range(start='2023-01-01', periods=n_points, freq='h')
    return pd.DataFrame(data, index=index)

def test_bollinger_initialization():
    """Testa l'inizializzazione del gene Bollinger."""
    # Test inizializzazione con config di default
    gene = BollingerGene()
    assert gene.period == 20
    assert gene.std_dev == 2.0
    assert gene.signal_threshold == 0.8
    assert gene.weight == 1.0
    
    # Test inizializzazione con config custom
    config = {
        'period': 10,
        'num_std': 1.5,
        'signal_threshold': 0.7,
        'weight': 0.8
    }
    gene = BollingerGene(config)
    assert gene.period == 10
    assert gene.std_dev == 1.5
    assert gene.signal_threshold == 0.7
    assert gene.weight == 0.8

def test_bollinger_calculation(sample_data):
    """Testa il calcolo delle bande di Bollinger."""
    gene = BollingerGene()
    bands = gene.calculate(sample_data)
    
    # Verifica presenza delle bande
    assert 'middle' in bands
    assert 'upper' in bands
    assert 'lower' in bands
    
    # Verifica dimensioni output
    assert len(bands['middle']) == len(sample_data)
    assert len(bands['upper']) == len(sample_data)
    assert len(bands['lower']) == len(sample_data)
    
    # Verifica relazioni tra bande
    assert np.all(bands['upper'] >= bands['middle'])
    assert np.all(bands['middle'] >= bands['lower'])
    
    # Verifica primi valori (dovrebbero essere 0 fino a period-1)
    assert np.all(bands['middle'][:gene.period-1] == 0)
    assert np.all(bands['upper'][:gene.period-1] == 0)
    assert np.all(bands['lower'][:gene.period-1] == 0)

def test_bollinger_signal_generation(sample_data):
    """Testa la generazione dei segnali."""
    # Usa un periodo più breve per il test
    config = {'period': 10}
    gene = BollingerGene(config)
    
    # Test iniziale
    signal = gene.generate_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Test con prezzo sopra upper band
    high_price = sample_data.copy()
    # Modifica solo l'ultimo prezzo
    for col in ['open', 'high', 'low', 'close']:
        high_price.loc[high_price.index[-1], col] *= 1.2
    
    # Verifica che il prezzo sia effettivamente sopra la upper band
    bands = gene.calculate(high_price)
    assert high_price['close'].iloc[-1] > bands['upper'][-1], \
        f"Prezzo {high_price['close'].iloc[-1]} non sopra upper band {bands['upper'][-1]}"
    
    signal = gene.generate_signal(high_price)
    assert signal < 0, f"Prezzo: {high_price['close'].iloc[-1]}, Upper: {bands['upper'][-1]}"
    
    # Test con prezzo sotto lower band
    low_price = sample_data.copy()
    # Modifica solo l'ultimo prezzo
    for col in ['open', 'high', 'low', 'close']:
        low_price.loc[low_price.index[-1], col] *= 0.8
    
    # Verifica che il prezzo sia effettivamente sotto la lower band
    bands = gene.calculate(low_price)
    assert low_price['close'].iloc[-1] < bands['lower'][-1], \
        f"Prezzo {low_price['close'].iloc[-1]} non sotto lower band {bands['lower'][-1]}"
    
    signal = gene.generate_signal(low_price)
    assert signal > 0, f"Prezzo: {low_price['close'].iloc[-1]}, Lower: {bands['lower'][-1]}"

def test_bollinger_edge_cases():
    """Testa i casi limite."""
    gene = BollingerGene()
    
    # Test con dati insufficienti
    short_data = pd.DataFrame({
        'close': [100, 101, 102]
    })
    signal = gene.generate_signal(short_data)
    assert signal == 0  # Dovrebbe restituire segnale neutro
    
    # Test con prezzi costanti
    flat_data = pd.DataFrame({
        'close': [100] * 30
    })
    signal = gene.generate_signal(flat_data)
    assert signal == 0  # Dovrebbe restituire segnale neutro con bandwidth zero
    
    # Test con dati mancanti
    with pytest.raises(ValueError):
        gene.generate_signal(pd.DataFrame())

def test_bollinger_bandwidth():
    """Testa il calcolo della bandwidth."""
    gene = BollingerGene()
    
    # Test caso normale
    bandwidth = gene._calculate_bandwidth(100, 110, 90)
    assert bandwidth == 0.2
    
    # Test con middle zero
    bandwidth = gene._calculate_bandwidth(0, 10, -10)
    assert bandwidth == 0
    
    # Test con bande identiche
    bandwidth = gene._calculate_bandwidth(100, 100, 100)
    assert bandwidth == 0

def test_bollinger_percent_b():
    """Testa il calcolo del %B."""
    gene = BollingerGene()
    
    # Test caso normale
    percent_b = gene._calculate_percent_b(100, 110, 90)
    assert percent_b == 0.5  # Prezzo a metà tra le bande
    
    # Test prezzo all'upper band
    percent_b = gene._calculate_percent_b(110, 110, 90)
    assert percent_b == 1.0
    
    # Test prezzo al lower band
    percent_b = gene._calculate_percent_b(90, 110, 90)
    assert percent_b == 0.0
    
    # Test con bande identiche
    percent_b = gene._calculate_percent_b(100, 100, 100)
    assert percent_b == 0.5  # Dovrebbe restituire 0.5 come valore di default
