# DNA System

## Scopo
Core del sistema che codifica le strategie di trading e gestisce l'evoluzione delle stesse attraverso pattern genetici.

## Struttura
```
core/
├── dna/
│   ├── __init__.py
│   └── base.py         # Classi base Gene e DNA
├── metrics/
│   ├── __init__.py
│   ├── gene_metrics.py      # Metriche per geni
│   ├── strategy_metrics.py  # Metriche per strategie
│   └── performance_metrics.py # Metriche sistema
```

## Funzionalità
1. **Codifica Strategie**
   - Traduzione pattern di mercato in sequenze DNA
   - Mappatura indicatori tecnici come geni
   - Struttura gerarchica delle strategie
   - Auto-tuning dei parametri

2. **Pattern Recognition**
   - Identificazione pattern ricorrenti
   - Analisi serie temporali
   - Correlazione pattern-risultati
   - Metriche di qualità pattern

3. **Indicatori Tecnici**
   - RSI come gene di momentum
   - MACD come gene di trend
   - Bollinger come gene di volatilità
   - Volume come gene di conferma

4. **Sistema di Metriche**
   - Gene Metrics:
     ```python
     {
         'win_rate': float,        # Tasso vittorie
         'profit_factor': float,   # Fattore profitto
         'accuracy': float,        # Precisione segnali
         'noise_ratio': float,     # Rapporto rumore
         'stability': float,       # Stabilità segnali
         'robustness': float,      # Robustezza
         'sensitivity': float,     # Sensibilità mercato
         'fitness': float          # Score complessivo
     }
     ```
   - Strategy Metrics:
     ```python
     {
         'total_return': float,    # Rendimento totale
         'sharpe_ratio': float,    # Sharpe ratio
         'sortino_ratio': float,   # Sortino ratio
         'max_drawdown': float,    # Massimo drawdown
         'win_rate': float,        # Tasso vittorie
         'profit_factor': float,   # Fattore profitto
         'market_correlation': float, # Correlazione mercato
         'strategy_fitness': float  # Score strategia
     }
     ```
   - Performance Metrics:
     ```python
     {
         'cpu_usage': float,       # Utilizzo CPU
         'memory_usage': float,    # Utilizzo memoria
         'signal_latency': float,  # Latenza segnali
         'execution_latency': float, # Latenza esecuzione
         'signals_per_second': float, # Throughput segnali
         'health_score': float     # Score salute sistema
     }
     ```

## Interazioni
- Riceve dati dal Sistema Nervoso
- Comunica con Sistema Riproduttivo per evoluzione
- Invia segnali al Sistema Endocrino
- Riceve feedback dal Sistema Immunitario

## Ottimizzazione
- Gene weights basati su fitness storica
- Pattern thresholds adattivi
- Parametri strategia auto-tuning
- Bilanciamento exploration/exploitation

### Dashboard Metrics
```
DNA Health Score: 0.85
├── Gene Performance
│   ├── Fitness: 0.78
│   ├── Stability: 0.82
│   └── Robustness: 0.75
├── Strategy Performance
│   ├── Returns: 0.92
│   ├── Risk: 0.85
│   └── Quality: 0.88
└── System Performance
    ├── Latency: 0.95
    ├── Throughput: 0.82
    └── Resources: 0.88
```

## Test Coverage
- Test unitari per ogni componente
- Test integrazione tra moduli
- Test performance con dati reali
- Validazione metriche

## CLI Interface
```bash
# Inizializzazione DNA
python main.py dna init

# Analisi pattern
python main.py dna analyze

# Gestione indicatori
python main.py dna indicators

# Sistema scoring
python main.py dna score
```

## Configurazione
```yaml
dna:
  indicators:
    rsi:
      period: 14
      overbought: 70
      oversold: 30
    macd:
      fast_period: 12
      slow_period: 26
      signal_period: 9
    bollinger:
      period: 20
      std_dev: 2
  optimization:
    population_size: 100
    generations: 50
    mutation_rate: 0.1
  metrics:
    window_size: 100
    update_interval: 1000
