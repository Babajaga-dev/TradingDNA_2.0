"""
TradingDNA 2.0 - Setup e Documentazione Iniziale
"""
import os
from pathlib import Path

def create_project_structure():
    """
    Crea la struttura base del progetto TradingDNA 2.0
    
    Struttura:
    TradingDNA_2.0/
    ├── config/          # File di configurazione
    ├── core/            # Componenti core
    ├── data/            # Database e cache
    ├── logs/            # Log per modulo
    ├── tests/           # Test unitari
    ├── utils/           # Utility condivise
    └── documents/       # Documentazione
    """
    # Definizione directory base
    directories = [
        'config',
        'core',
        'data',
        'logs',
        'tests',
        'utils',
        'documents'
    ]
    
    # Creazione directory
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        
    print("✓ Struttura directory creata")

def create_readme():
    """
    Crea il README principale del progetto con la documentazione completa
    """
    readme_content = """# TradingDNA 2.0

## Scopo del Progetto
Sistema di trading algoritmico che simula un organismo biologico per l'analisi e la predizione 
del mercato delle criptovalute.

### Componenti Biologici
1. **DNA**
   - Core del sistema
   - Codifica strategie di trading
   - Pattern recognition
   - Indicatori tecnici come geni

2. **Sistema Immunitario**
   - Gestione rischi
   - Stop-loss dinamici
   - Protezione da eventi estremi
   - Filtri anti-noise

3. **Metabolismo**
   - Gestione capitale
   - Sizing posizioni
   - Ottimizzazione risorse
   - Bilanciamento portfolio

4. **Sistema Nervoso**
   - Acquisizione dati real-time
   - Preprocessamento
   - Pattern recognition
   - Analisi tecnica

5. **Sistema Endocrino**
   - Stato del mercato
   - Adattamento parametri
   - Feedback loop
   - Gestione emozioni trading

6. **Sistema Riproduttivo**
   - Evoluzione strategie
   - Algoritmi genetici
   - Ottimizzazione parametri
   - Selezione naturale

## Piano di Sviluppo

### Step 1: Architettura Base
- ✓ Struttura directory (max 2 livelli)
- ✓ Setup iniziale progetto
- ✓ Definizione interfacce base
- ✓ Struttura modulare

### Step 2: Sistema Configurazione
- ✓ Configuration Manager
- ✓ File YAML separati per:
  - Network (exchange, pairs)
  - Trace (logging)
  - Portfolio (risk, capital)
- ✓ No hardcoding
- ✓ Interfacce configurazione

### Step 3: Sistema Logging
- ✓ Log indipendenti per modulo
- ✓ Configurazione granulare
- ✓ Console/File logging
- ✓ Rotazione automatica

### Step 4: Componenti Core (In Progress)
- ⚪ Implementazione DNA
- ⚪ Sistema immunitario
- ⚪ Metabolismo
- ⚪ Sistema nervoso

### Step 5: Strategie Trading (Pianificato)
- ⚪ Implementazione indicatori
- ⚪ Strategie base
- ⚪ Sistema evoluzione
- ⚪ Backtesting

### Step 6: Testing (Pianificato)
- ⚪ Unit testing
- ⚪ Integration testing
- ⚪ Performance testing
- ⚪ Ottimizzazione

## Coding Rules

### 1. Limiti Strutturali
- File max 400 righe
- Directory max 2 livelli
- Un modulo per file
- Nomi descrittivi snake_case

### 2. Configurazione
- No hardcoding
- Parametri in YAML
- Uso Configuration Manager
- Validazione parametri

### 3. Logging
- Logger per modulo
- Configurazione indipendente
- Messaggi chiari
- Livelli appropriati

### 4. Codice
- Docstring complete
- Type hints
- Nomi descrittivi
- Test unitari
- Coverage 80%+

### 5. Git
- Commit atomici
- Messaggi descrittivi
- Feature branch
- Code review

## Stack Tecnologico
- Python 3.9+
- SQLite
- YAML config
- CLI interface

## Struttura File

```
TradingDNA_2.0/
├── config/
│   ├── network.yaml     # Config exchange
│   ├── trace.yaml      # Config logging
│   └── portfolio.yaml  # Config trading
├── core/
│   ├── dna_base.py
│   ├── dna_genes.py
│   ├── immune_check.py
│   ├── immune_protect.py
│   ├── metab_capital.py
│   ├── metab_position.py
│   ├── nerve_fetch.py
│   └── nerve_process.py
├── data/
│   ├── market_data.db  # SQLite database
│   └── cache/         # Cache directory
├── logs/
│   ├── dna.log
│   ├── immune.log
│   ├── metabolism.log
│   └── nervous.log
├── tests/
│   ├── test_dna.py
│   ├── test_immune.py
│   └── test_utils.py
├── utils/
│   ├── logger.py
│   ├── database.py
│   └── validators.py
└── setup.py          # Questo file
```
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("✓ README creato")

def main():
    """
    Funzione principale per il setup del progetto
    """
    print("Inizializzazione TradingDNA 2.0...")
    create_project_structure()
    create_readme()
    print("\nSetup completato! Struttura progetto creata e documentazione generata.")

if __name__ == "__main__":
    main()
