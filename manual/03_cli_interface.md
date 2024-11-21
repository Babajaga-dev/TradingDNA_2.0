# Interfaccia CLI

## Gestione Log
```bash
# Visualizza log
python main.py log show

# Filtra log per livello
python main.py log show --level ERROR

# Filtra log per componente
python main.py log show --component DNA

# Filtra per periodo
python main.py log show --start 2024-01-01 --end 2024-01-31

# Esporta log
python main.py log export logs.txt

# Pulisci log vecchi
python main.py log clean --older-than 30d
```

## Download Dati
```bash
# Download dati di mercato
python main.py download market --pair BTC/USDT --timeframe 1h

# Download dati con periodo specifico
python main.py download market --pair ETH/USDT --timeframe 4h --start 2023-01-01

# Download dati con formato specifico
python main.py download market --pair BTC/USDT --timeframe 1d --format parquet

# Download multipli pairs
python main.py download market --pairs BTC/USDT,ETH/USDT --timeframe 1h

# Verifica integrità dati
python main.py download verify --pair BTC/USDT
```

## Comandi DNA
```bash
# Inizializza il sistema DNA
python main.py dna init

# Analizza pattern su una coppia
python main.py dna analyze --pair BTC/USDT --timeframe 1h

# Visualizza scoring DNA
python main.py dna score

# Analisi con parametri personalizzati
python main.py dna analyze --pair ETH/USDT --min-confidence 0.8 --max-patterns 500

# Esporta pattern trovati
python main.py dna export-patterns patterns.json

# Training pattern recognition
python main.py dna train --pair BTC/USDT --epochs 100
```

## Gestione Sistema

### Sistema Immunitario
```bash
# Avvia analisi rischi
python main.py immune

# Configura parametri rischio
python main.py immune config --max-risk 0.02

# Report rischi
python main.py immune report
```

### Sistema Metabolico
```bash
# Analisi capitale
python main.py metabolism

# Ottimizza allocazione
python main.py metabolism optimize

# Report performance
python main.py metabolism report
```

### Sistema Nervoso
```bash
# Analisi dati real-time
python main.py nervous

# Configura alerting
python main.py nervous alerts --enable

# Monitor mercato
python main.py nervous monitor --pair BTC/USDT
```

### Sistema Endocrino
```bash
# Ottimizzazione parametri
python main.py endocrine

# Adatta parametri
python main.py endocrine adapt

# Report adattamento
python main.py endocrine report
```

### Sistema Riproduttivo
```bash
# Evoluzione strategie
python main.py reproductive

# Training strategie
python main.py reproductive train

# Report evoluzione
python main.py reproductive report
```

## Opzioni Globali

Tutti i comandi supportano le seguenti opzioni globali:

| Opzione | Descrizione |
|---------|-------------|
| --verbose | Output dettagliato |
| --quiet | Minimizza output |
| --config FILE | File config custom |
| --log-level LVL | Livello log |
| --no-color | Disabilita colori |
| --json | Output in JSON |
| --help | Mostra aiuto |
