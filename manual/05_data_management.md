# Gestione Dati

## Struttura Dati

Il sistema gestisce automaticamente i dataset divisi in:
- Training (70%)
- Validazione (15%)
- Testing (15%)

### Directory Structure
```
data/market/
├── BTC_USDT_1h_training.parquet
├── BTC_USDT_1h_validation.parquet
├── BTC_USDT_1h_testing.parquet
└── ...
```

## Timeframes Supportati

| Timeframe | Descrizione | Uso Tipico |
|-----------|-------------|------------|
| 1m | 1 minuto | Trading ad alta frequenza |
| 5m | 5 minuti | Scalping |
| 15m | 15 minuti | Intraday trading |
| 1h | 1 ora | Swing trading |
| 4h | 4 ore | Trend following |
| 1d | 1 giorno | Position trading |

## Formato Dati

### Parquet
Il sistema utilizza il formato Parquet per l'archiviazione dei dati, che offre:
- Compressione efficiente
- Lettura colonnare
- Performance ottimizzata
- Schema integrato

### Schema Dati
```
- timestamp (datetime64[ns])
- open (float64)
- high (float64)
- low (float64)
- close (float64)
- volume (float64)
```

## Download Dati

### Comandi Base
```bash
# Download singolo pair
python main.py download market --pair BTC/USDT --timeframe 1h

# Download multipli pairs
python main.py download market --pairs BTC/USDT,ETH/USDT --timeframe 1h

# Download con periodo specifico
python main.py download market --pair ETH/USDT --timeframe 4h --start 2023-01-01
```

### Opzioni Download

| Opzione | Descrizione |
|---------|-------------|
| --start | Data inizio (YYYY-MM-DD) |
| --end | Data fine (YYYY-MM-DD) |
| --format | Formato output (parquet/csv) |
| --force | Forza riscrittura |
| --verify | Verifica integrità |

## Validazione Dati

Il sistema esegue automaticamente le seguenti verifiche:
1. **Completezza**
   - Nessun dato mancante
   - Serie temporale continua
   - Volumi validi

2. **Qualità**
   - Prezzi validi (> 0)
   - High > Low
   - Open/Close tra High/Low

3. **Integrità**
   - Timestamp ordinati
   - No duplicati
   - Formato corretto

## Gestione Cache

### Configurazione Cache
```yaml
cache:
  enabled: true
  size: 1000
  ttl: 3600  # secondi
  cleanup_interval: 300  # secondi
```

### Politiche Cache
- Least Recently Used (LRU)
- Time-based expiration
- Size-based eviction

## Backup e Ripristino

### Backup Dati
```bash
# Backup completo
python main.py data backup

# Backup selettivo
python main.py data backup --pairs BTC/USDT --timeframes 1h,4h

# Backup compresso
python main.py data backup --compress
```

### Ripristino Dati
```bash
# Ripristino completo
python main.py data restore backup.zip

# Ripristino selettivo
python main.py data restore backup.zip --pairs BTC/USDT

# Verifica dopo ripristino
python main.py data verify
```

## Manutenzione Dati

### Pulizia
```bash
# Rimuovi dati vecchi
python main.py data clean --older-than 90d

# Ottimizza storage
python main.py data optimize

# Rimuovi dati corrotti
python main.py data clean --corrupted
```

### Verifica
```bash
# Verifica integrità
python main.py data verify

# Report stato
python main.py data status

# Analisi spazio
python main.py data analyze-space
