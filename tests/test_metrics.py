"""Test per il sistema di metriche.

Verifica il funzionamento delle metriche per geni, strategie e performance.
"""
import time
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from core.metrics import GeneMetrics, StrategyMetrics, PerformanceMetrics

@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Carica dati di test da file parquet."""
    data_path = Path(__file__).parent.parent / "data/market/BTC_USDT_1h_training.parquet"
    return pd.read_parquet(data_path)

def test_gene_metrics():
    """Verifica calcolo metriche gene."""
    metrics = GeneMetrics(
        win_rate=0.7,
        profit_factor=1.5,
        accuracy=0.8,
        noise_ratio=0.2,
        stability=0.9,
        robustness=0.85
    )
    
    # Verifica fitness score
    fitness = metrics.calculate_fitness()
    assert 0 <= fitness <= 1
    
    # Verifica conversione a dict
    metrics_dict = metrics.to_dict()
    assert all(key in metrics_dict for key in [
        'win_rate', 'profit_factor', 'accuracy', 'noise_ratio',
        'stability', 'robustness', 'fitness'
    ])
    
    # Verifica aggiornamento metriche
    new_results = {'win_rate': 0.75, 'profit_factor': 1.8}
    metrics.update(new_results)
    assert metrics.win_rate == 0.75
    assert metrics.profit_factor == 1.8
    
    # Verifica metriche auto-tuning
    signals = np.array([0.1, 0.2, 0.15, 0.18, 0.22])
    metrics.calculate_auto_tuning_metrics(signals)
    assert 0 <= metrics.stability <= 1
    assert 0 <= metrics.sensitivity <= 1
    assert 0 <= metrics.robustness <= 1

def test_strategy_metrics(sample_data):
    """Verifica calcolo metriche strategia."""
    metrics = StrategyMetrics()
    
    # Simula una curva equity
    equity_curve = np.cumsum(np.random.normal(0.001, 0.02, len(sample_data)))
    equity_curve = np.exp(equity_curve)  # Converte in rendimenti cumulativi
    
    # Verifica metriche rendimenti
    metrics.calculate_returns_metrics(equity_curve)
    assert isinstance(metrics.total_return, float)
    assert isinstance(metrics.sharpe_ratio, float)
    assert isinstance(metrics.sortino_ratio, float)
    
    # Verifica metriche rischio
    metrics.calculate_risk_metrics(equity_curve)
    assert metrics.max_drawdown <= 0
    assert isinstance(metrics.var_95, float)
    
    # Verifica metriche trade
    trades = [
        {'profit': 100}, {'profit': -50}, {'profit': 80},
        {'profit': 120}, {'profit': -30}
    ]
    metrics.calculate_trade_metrics(trades)
    assert metrics.win_rate == 0.6  # 3 vincenti su 5
    assert metrics.profit_factor > 1  # Profitti > Perdite
    
    # Verifica metriche qualità
    market_returns = np.random.normal(0.001, 0.02, len(equity_curve))
    strategy_returns = np.diff(equity_curve) / equity_curve[:-1]
    metrics.calculate_quality_metrics(strategy_returns, market_returns)
    assert -1 <= metrics.market_correlation <= 1
    assert isinstance(metrics.strategy_fitness, float)
    
    # Verifica conversione a dict
    metrics_dict = metrics.to_dict()
    assert all(key in metrics_dict for key in [
        'total_return', 'sharpe_ratio', 'max_drawdown',
        'win_rate', 'profit_factor', 'strategy_fitness'
    ])

def test_performance_metrics():
    """Verifica calcolo metriche performance."""
    metrics = PerformanceMetrics(window_size=10)
    
    # Verifica metriche sistema
    metrics.update_system_metrics()
    assert 0 <= metrics.cpu_usage <= 100
    assert 0 <= metrics.memory_usage <= 100
    assert isinstance(metrics.disk_io, (int, float))
    
    # Verifica metriche latenza
    metrics.record_signal_latency(10.5)  # ms
    metrics.record_signal_latency(12.3)
    assert metrics.signal_latency > 0
    
    metrics.record_execution_latency(50.2)  # ms
    metrics.record_execution_latency(48.7)
    assert metrics.execution_latency > 0
    assert metrics.total_latency == metrics.signal_latency + metrics.execution_latency
    
    # Verifica statistiche latenza
    latency_stats = metrics.get_latency_stats()
    assert all(key in latency_stats for key in [
        'signal_latency', 'execution_latency', 'total_latency'
    ])
    
    # Verifica health score
    health_score = metrics.get_health_score()
    assert 0 <= health_score <= 1
    
    # Verifica conversione a dict
    metrics_dict = metrics.to_dict()
    assert all(key in metrics_dict for key in [
        'cpu_usage', 'memory_usage', 'disk_io',
        'signal_latency', 'execution_latency', 'total_latency',
        'signals_per_second', 'trades_per_second'
    ])

def test_metrics_integration(sample_data):
    """Verifica integrazione tra i diversi tipi di metriche."""
    gene_metrics = GeneMetrics()
    strategy_metrics = StrategyMetrics()
    performance_metrics = PerformanceMetrics()
    
    # Simula operazioni di trading
    for i in range(len(sample_data)):
        # Simula generazione segnale
        start_time = time.time()
        signal = np.random.choice([-1, 0, 1])
        performance_metrics.record_signal_latency((time.time() - start_time) * 1000)
        
        # Aggiorna metriche gene
        if i > 0:
            returns = sample_data['close'].pct_change().iloc[i]
            profit = signal * returns
            gene_metrics.update({
                'win_rate': 1.0 if profit > 0 else 0.0,
                'profit_factor': abs(profit) if profit > 0 else 1/abs(profit) if profit < 0 else 1.0
            })
    
    # Verifica che tutte le metriche siano state aggiornate
    assert gene_metrics.calculate_fitness() >= 0
    assert performance_metrics.get_health_score() >= 0
    
    # Verifica che le metriche siano coerenti
    gene_dict = gene_metrics.to_dict()
    perf_dict = performance_metrics.to_dict()
    
    assert 0 <= gene_dict['win_rate'] <= 1
    assert perf_dict['total_latency'] >= 0
