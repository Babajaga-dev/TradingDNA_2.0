# DNA System

## Scopo
Core del sistema che codifica le strategie di trading e gestisce l'evoluzione delle stesse attraverso pattern genetici.

## Struttura
```
core/
├── dna/
│   ├── __init__.py
│   ├── dna.py           # Classe DNA singleton
│   ├── gene.py          # Classe base Gene
│   ├── rsi_gene.py      # Gene RSI
│   ├── macd_gene.py     # Gene MACD
│   ├── bollinger_gene.py # Gene Bollinger
│   ├── volume_gene.py    # Gene Volume
│   └── pattern_recognition.py # Pattern Recognition
├── metrics/
│   ├── __init__.py
│   ├── gene_metrics.py      # Metriche per geni
│   ├── strategy_metrics.py  # Metriche per strategie
│   └── performance_metrics.py # Metriche sistema
cli/
├── handlers/
│   ├── dna_handler.py     # Handler principale DNA
│   ├── dna_analysis.py    # Analisi geni
│   └── dna_optimization.py # Ottimizzazione
```

## Architettura
1. **Pattern Singleton**
   - Istanza DNA unica e persistente
   - Stato salvato automaticamente
   - Configurazione centralizzata YAML
   - Inizializzazione lazy loading

2. **Modularizzazione**
   - Handler separati per responsabilità
   - Limite 400 righe per file
   - Logging dedicato per modulo
   - Progress bars e feedback visuale

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

# Analisi singolo gene
python main.py dna gene --type rsi
python main.py dna gene --type macd
python main.py dna gene --type bollinger
python main.py dna gene --type volume

# Ottimizzazione parametri
python main.py dna optimize

# Validazione strategia
python main.py dna validate

# Composizione segnali
python main.py dna compose
```

## Configurazione
```yaml
dna:
  indicators:
    pattern_recognition:
      min_pattern_length: 5
      max_pattern_length: 20
      min_confidence: 0.7
      similarity_threshold: 0.8
      
    rsi:
      period: 14
      overbought: 70
      oversold: 30
      signal_threshold: 0.6
      weight: 1.0

    macd:
      fast_period: 12
      slow_period: 26
      signal_period: 9
      signal_threshold: 0.6
      weight: 1.0

    bollinger:
      period: 20
      num_std: 2.0
      signal_threshold: 0.8
      weight: 1.0

    volume:
      vwap_period: 14
      volume_ma_period: 20
      signal_threshold: 0.6
      weight: 1.0
      
  optimization:
    method: "SLSQP"
    parallel: true
    max_workers: 4
    
  metrics:
    window_size: 100
    update_interval: 1000
```

## Persistenza
- Stato DNA salvato in data/dna_state.pkl
- Caricamento automatico all'inizializzazione
- Salvataggio dopo ogni modifica
- Backup automatico dello stato

## Regole Implementazione
1. **Struttura**
   - File max 400 righe
   - Directory max 2 livelli
   - Un modulo per file
   - snake_case per file/funzioni, PascalCase per classi

2. **Config**
   - No hardcoding
   - YAML per config
   - Validazione parametri
   - ConfigManager centralizzato

3. **Codice**
   - Type hints obbligatori
   - Docstrings complete
   - Test coverage 80%+
   - Logging per modulo

4. **Visual**
   - Progress bars
   - Dashboard realtime
   - Log visuali
   - Alert system
