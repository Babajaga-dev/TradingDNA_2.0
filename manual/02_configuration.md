# Configurazione

Il sistema utilizza file YAML per la configurazione centralizzata. I principali file di configurazione si trovano nella directory `config/`:

## File di Configurazione

### DNA Configuration (dna.yaml)
```yaml
general:
  name: "TradingDNA 2.0"
  version: "2.0.0"

data:
  split_ratios:
    training: 0.7
    validation: 0.15
    testing: 0.15

indicators:
  pattern_recognition:
    min_pattern_length: 5
    max_pattern_length: 20
    min_confidence: 0.7
    similarity_threshold: 0.8
```

### Network Configuration (network.yaml)
- Configurazione delle connessioni di rete
- Parametri API exchange
- Rate limiting
- Timeout e retry

### Portfolio Configuration (portfolio.yaml)
- Asset allocation
- Risk management
- Position sizing
- Trading pairs

### Trace Configuration (trace.yaml)
- Log levels
- Debug settings
- Performance tracking
- Metrics collection

## Gestione Configurazione via CLI

```bash
# Visualizza configurazione corrente
python main.py config show

# Modifica un valore di configurazione
python main.py config set data.split_ratios.training 0.8

# Ripristina configurazione di default
python main.py config reset

# Valida configurazione
python main.py config validate

# Esporta configurazione
python main.py config export config_backup.yaml

# Importa configurazione
python main.py config import config_backup.yaml
```

## Parametri Configurabili

### Pattern Recognition
| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| min_pattern_length | 5 | Lunghezza minima pattern |
| max_pattern_length | 20 | Lunghezza massima pattern |
| min_confidence | 0.7 | Soglia minima confidenza |
| similarity_threshold | 0.8 | Soglia similarità |

### Data Management
| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| training_ratio | 0.7 | % dati per training |
| validation_ratio | 0.15 | % dati per validazione |
| testing_ratio | 0.15 | % dati per testing |

### Performance
| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| max_cpu_usage | 80 | Limite CPU (%) |
| max_memory | 2048 | Limite RAM (MB) |
| cache_size | 1000 | Dimensione cache |
