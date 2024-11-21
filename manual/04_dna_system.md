# Sistema DNA

Il sistema DNA è il core dell'analisi tecnica e del pattern recognition di TradingDNA 2.0.

## Pattern Recognition

### Parametri Pattern Recognition

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| min_pattern_length | 5 | Lunghezza minima pattern in candele |
| max_pattern_length | 20 | Lunghezza massima pattern in candele |
| min_confidence | 0.7 | Soglia minima di confidenza |
| similarity_threshold | 0.8 | Soglia di similarità tra pattern |
| correlation_weight | 0.4 | Peso della correlazione nel calcolo |
| length_weight | 0.2 | Peso della lunghezza nel calcolo |
| quality_threshold | 0.6 | Soglia minima di qualità |
| max_patterns | 1000 | Numero massimo di pattern memorizzati |

### Algoritmo di Pattern Recognition

Il sistema utilizza un algoritmo sofisticato per il riconoscimento dei pattern che include:

1. **Normalizzazione dei Dati**
   - Standardizzazione delle serie temporali
   - Rimozione del rumore
   - Gestione valori mancanti

2. **Identificazione Pattern**
   - Sliding window di dimensione variabile
   - Calcolo similarità tra sequenze
   - Clustering pattern simili

3. **Scoring Pattern**
   - Correlazione con pattern noti
   - Valutazione lunghezza pattern
   - Calcolo confidenza complessiva

4. **Validazione Pattern**
   - Test su dati storici
   - Verifica robustezza
   - Analisi falsi positivi

## Metriche DNA

### Metriche di Performance

#### Metriche di Sistema
- CPU Usage (%)
- Memory Usage (%)
- Disk I/O

#### Metriche di Latenza
- Signal Latency (ms)
- Execution Latency (ms)
- Total Latency (ms)

#### Metriche di Throughput
- Signals per Second
- Trades per Second

### Metriche di Trading

#### Metriche di Rendimento
- Total Return
- Annual Return
- Volatility
- Sharpe Ratio
- Sortino Ratio

#### Metriche di Rischio
- Maximum Drawdown
- Average Drawdown
- Drawdown Duration
- Value at Risk (95%)

#### Metriche Operative
- Win Rate
- Profit Factor
- Average Trade
- Number of Trades

#### Metriche di Qualità
- Strategy Fitness
- Market Correlation
- Alpha
- Beta

## Health Score

Il sistema calcola uno score di salute (0-1) basato su:
- CPU Usage (peso: 0.3)
- Memory Usage (peso: 0.2)
- Latency (peso: 0.5)

Formula:
```
health_score = (0.3 * cpu_score + 0.2 * memory_score + 0.5 * latency_score)

dove:
cpu_score = 1 - (cpu_usage / 100)
memory_score = 1 - (memory_usage / 100)
latency_score = 1 - (total_latency / 1000)
```

## Strategy Fitness

Il fitness di una strategia è calcolato considerando:
- Sharpe Ratio (peso: 0.2)
- Sortino Ratio (peso: 0.2)
- Profit Factor (peso: 0.2)
- Win Rate (peso: 0.15)
- Max Drawdown (peso: 0.15)
- Market Correlation (peso: 0.1)

Formula:
```
strategy_fitness = Σ(metric_normalized * weight)

dove metric_normalized è il valore normalizzato (0-1) di ogni metrica
```

## Utilizzo via CLI

```bash
# Inizializza DNA
python main.py dna init

# Analisi pattern
python main.py dna analyze --pair BTC/USDT --timeframe 1h

# Visualizza metriche
python main.py dna metrics

# Esporta pattern
python main.py dna export-patterns output.json

# Training sistema
python main.py dna train --epochs 100

# Ottimizzazione parametri
python main.py dna optimize
