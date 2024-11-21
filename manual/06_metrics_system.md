# Sistema di Metriche

## Metriche di Performance

### Metriche di Sistema
```python
class PerformanceMetrics:
    cpu_usage: float      # Utilizzo CPU in %
    memory_usage: float   # Utilizzo memoria in %
    disk_io: float       # I/O disco in bytes
```

#### Monitoraggio Sistema
- CPU Usage: Monitoraggio real-time dell'utilizzo CPU
- Memory Usage: Tracciamento consumo memoria
- Disk I/O: Monitoraggio operazioni I/O

### Metriche di Latenza
```python
signal_latency: float    # Latenza generazione segnali
execution_latency: float # Latenza esecuzione
total_latency: float     # Latenza totale
```

#### Statistiche Latenza
- Min/Max/Avg latenza segnali
- Min/Max/Avg latenza esecuzione
- Deviazione standard latenza

### Metriche di Throughput
```python
signals_per_second: float # Segnali processati/secondo
trades_per_second: float  # Trade eseguiti/secondo
```

## Metriche di Trading

### Metriche di Rendimento
```python
class StrategyMetrics:
    total_return: float    # Rendimento totale
    annual_return: float   # Rendimento annualizzato
    volatility: float      # Volatilità
    sharpe_ratio: float    # Sharpe Ratio
    sortino_ratio: float   # Sortino Ratio
```

#### Calcolo Rendimenti
```python
# Rendimento totale
total_return = (equity_final / equity_initial) - 1

# Rendimento annualizzato
annual_return = (1 + total_return) ** (252 / days) - 1

# Volatilità
volatility = np.std(returns) * np.sqrt(252)

# Sharpe Ratio
sharpe_ratio = (annual_return - risk_free_rate) / volatility

# Sortino Ratio
downside_returns = returns[returns < 0]
downside_vol = np.std(downside_returns) * np.sqrt(252)
sortino_ratio = (annual_return - risk_free_rate) / downside_vol
```

### Metriche di Rischio
```python
max_drawdown: float      # Massimo drawdown
avg_drawdown: float      # Drawdown medio
drawdown_duration: float # Durata drawdown
var_95: float           # Value at Risk 95%
```

#### Calcolo Drawdown
```python
# Massimo drawdown
peak = np.maximum.accumulate(equity_curve)
drawdown = (equity_curve - peak) / peak
max_drawdown = np.min(drawdown)

# Drawdown medio
avg_drawdown = np.mean(drawdown[drawdown < 0])

# Durata drawdown
underwater = drawdown < 0
drawdown_duration = np.mean(underwater_periods == -1)
```

### Metriche Operative
```python
win_rate: float         # % trade vincenti
profit_factor: float    # Rapporto profitti/perdite
avg_trade: float        # Profitto medio per trade
num_trades: int         # Numero totale trade
```

#### Calcolo Metriche Operative
```python
# Win rate
win_rate = len(winning_trades) / num_trades

# Profit factor
profit_factor = total_profit / abs(total_loss)

# Profitto medio
avg_trade = np.mean(profits)
```

### Metriche di Qualità
```python
strategy_fitness: float    # Fitness complessivo
market_correlation: float  # Correlazione col mercato
alpha: float              # Alpha
beta: float               # Beta
```

## Health Score

### Calcolo Health Score
```python
weights = {
    'cpu': 0.3,
    'memory': 0.2,
    'latency': 0.5
}

cpu_score = 1 - (cpu_usage / 100)
memory_score = 1 - (memory_usage / 100)
latency_score = 1 - (total_latency / 1000)

health_score = (
    weights['cpu'] * cpu_score +
    weights['memory'] * memory_score +
    weights['latency'] * latency_score
)
```

## Strategy Fitness

### Calcolo Strategy Fitness
```python
weights = {
    'sharpe_ratio': 0.2,
    'sortino_ratio': 0.2,
    'profit_factor': 0.2,
    'win_rate': 0.15,
    'max_drawdown': 0.15,
    'market_correlation': 0.1
}

normalized = {
    'sharpe_ratio': max(min(sharpe_ratio / 2, 1), 0),
    'sortino_ratio': max(min(sortino_ratio / 2, 1), 0),
    'profit_factor': max(min(profit_factor / 3, 1), 0),
    'win_rate': win_rate,
    'max_drawdown': max(min(-max_drawdown / 0.2, 1), 0),
    'market_correlation': max(min((1 - abs(market_correlation)) / 0.5, 1), 0)
}

strategy_fitness = sum(normalized[k] * v for k, v in weights.items())
```

## Utilizzo via CLI

```bash
# Visualizza tutte le metriche
python main.py metrics show

# Metriche sistema
python main.py metrics system

# Metriche trading
python main.py metrics trading

# Export metriche
python main.py metrics export --format json

# Monitoraggio real-time
python main.py metrics monitor --interval 5s

# Report dettagliato
python main.py metrics report --from 2024-01-01
