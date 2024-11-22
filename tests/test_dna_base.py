"""Test unitari per il DNA System.

Verifica il funzionamento delle classi base del DNA system usando dati reali.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from core.dna.gene import Gene
from core.dna.dna import DNA
from core.metrics.gene_metrics import GeneMetrics

class MockGene(Gene):
    """Gene di test che implementa RSI."""
    
    def calculate(self, data: pd.DataFrame) -> np.ndarray:
        """Calcola RSI sui dati."""
        close = data['close'].values
        delta = np.diff(close)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gain)
        avg_loss = np.mean(loss)
        
        if avg_loss == 0:
            return np.full_like(close, 50)
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return np.full_like(close, rsi)
        
    def generate_signal(self, data: pd.DataFrame) -> float:
        """Genera segnale basato su RSI."""
        rsi = self.calculate(data)[-1]
        
        if rsi > 70:
            return -1  # Sell
        elif rsi < 30:
            return 1   # Buy
        return 0      # Hold

@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Carica dati di test da file parquet."""
    data_path = Path(__file__).parent.parent / "data/market/BTC_USDT_1h_training.parquet"
    return pd.read_parquet(data_path)

@pytest.fixture
def mock_gene() -> MockGene:
    """Crea un gene di test."""
    return MockGene("RSI")

@pytest.fixture
def dna_system() -> DNA:
    """Crea un'istanza del DNA system."""
    return DNA()

def test_gene_metrics():
    """Verifica calcolo metriche gene."""
    metrics = GeneMetrics(
        win_rate=0.7,
        profit_factor=1.5,
        accuracy=0.8,
        noise_ratio=0.2
    )
    
    fitness = metrics.calculate_fitness()
    assert 0 <= fitness <= 1
    
    metrics_dict = metrics.to_dict()
    assert all(key in metrics_dict for key in [
        'win_rate', 'profit_factor', 'accuracy',
        'adaptation_speed', 'signal_strength', 'noise_ratio',
        'fitness'
    ])

def test_gene_calculation(mock_gene, sample_data):
    """Verifica calcolo indicatore su dati reali."""
    values = mock_gene.calculate(sample_data)
    assert len(values) == len(sample_data)
    assert all(0 <= v <= 100 for v in values)

def test_gene_signal_generation(mock_gene, sample_data):
    """Verifica generazione segnali su dati reali."""
    signal = mock_gene.generate_signal(sample_data)
    assert signal in [-1, 0, 1]

def test_dna_strategy(dna_system, mock_gene, sample_data):
    """Verifica funzionamento strategia DNA."""
    # Aggiunge gene al DNA
    dna_system.add_gene(mock_gene)
    assert mock_gene.name in dna_system.genes
    
    # Genera segnale strategia
    signal = dna_system.get_strategy_signal(sample_data)
    assert -1 <= signal <= 1
    
    # Rimuove gene
    dna_system.remove_gene(mock_gene.name)
    assert mock_gene.name not in dna_system.genes

def test_gene_metrics_update(mock_gene):
    """Verifica aggiornamento metriche gene."""
    results = {
        'win_rate': 0.75,
        'profit_factor': 1.8,
        'accuracy': 0.85,
        'noise_ratio': 0.15
    }
    
    mock_gene.update_metrics(results)
    metrics = mock_gene.metrics.to_dict()
    
    for key, value in results.items():
        assert metrics[key] == value

def test_empty_dna_strategy(dna_system, sample_data):
    """Verifica comportamento DNA senza geni."""
    signal = dna_system.get_strategy_signal(sample_data)
    assert signal == 0

def test_multiple_genes_strategy(dna_system, sample_data):
    """Verifica strategia con multipli geni."""
    # Crea due geni con metriche diverse
    gene1 = MockGene("RSI_1")
    gene1.update_metrics({'win_rate': 0.8, 'profit_factor': 2.0})
    
    gene2 = MockGene("RSI_2") 
    gene2.update_metrics({'win_rate': 0.6, 'profit_factor': 1.5})
    
    # Aggiunge entrambi i geni
    dna_system.add_gene(gene1)
    dna_system.add_gene(gene2)
    
    # Verifica segnale composito
    signal = dna_system.get_strategy_signal(sample_data)
    assert -1 <= signal <= 1
