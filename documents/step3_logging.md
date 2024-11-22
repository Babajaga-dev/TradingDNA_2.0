# Step 3: Sistema di Logging

## Obiettivi ✅
1. Logger indipendenti per modulo
2. Configurazione granulare
3. Visualizzazione avanzata
4. Integrazione con CLI

## Implementazione

### 1. Utilizzo Base
```python
from utils.logger_base import setup_logging, get_logger

# Inizializza il sistema di logging
setup_logging()

# Ottieni un logger base
logger = get_logger("my_module")
logger.info("Messaggio informativo")
logger.warning("Attenzione!")
logger.error("Errore critico")
```

### 2. Component Logger
```python
from utils.logger_base import get_component_logger

# Ottieni logger per componenti specifici
dna_logger = get_component_logger("dna")
immune_logger = get_component_logger("immune")

# Logging con icone e colori specifici
dna_logger.info("Analisi DNA in corso...")     # 🧬 DNA         │ Analisi DNA in corso...
immune_logger.warning("Anomalia rilevata")     # 🛡️ IMMUNE      │ Anomalia rilevata
```

### 3. Progress Tracking
```python
from utils.logger_base import get_progress_logger

# Progress bar singola
with get_progress_logger() as progress:
    task_id = progress.add_task("Download dati", total=100)
    for i in range(100):
        # Aggiorna progresso
        progress.update(task_id, advance=1)

# Progress bar multipla con logging
dna = get_component_logger("dna")
with get_progress_logger() as progress:
    analysis = progress.add_task("Analisi DNA", total=100)
    training = progress.add_task("Training modello", total=100)
    
    for i in range(100):
        progress.update(analysis, advance=1)
        if i % 10 == 0:
            dna.info(f"Completata analisi step {i}")
    
    for i in range(100):
        progress.update(training, advance=1)
```

## Configurazione YAML

### 1. Configurazione Base
```yaml
global:
  log_level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  encoding: "utf-8"

file:
  enabled: true
  path: "logs"
  max_size_mb: 10
  backup_count: 5
```

### 2. Configurazione Visual
```yaml
visual:
  enabled: true
  colors:
    info: "cyan"
    warning: "yellow"
    error: "red bold"
    success: "green bold"
  
  components:
    dna:
      icon: "🧬"
      color: "blue"
    immune:
      icon: "🛡️"
      color: "green"
```

## Esempi di Output

### 1. Component Status
```
🧬 DNA         │ Inizializzazione sistema...
├── Caricamento configurazione   [━━━━━━━━━━] 100%
├── Analisi dati storici        [━━━━━━━━━━] 100%
└── Training modello            [━━━━━━━━━━] 100%

🛡️ IMMUNE      │ Controllo sicurezza
├── Validazione input    [━━━━━━━━━━] 100%
├── Verifica limiti     [━━━━━━━━━━] 100%
└── Test connessione    [━━━━━━━━━━] 100%
```

### 2. Error Handling
```
❌ ERROR    │ Errore connessione exchange
├── Component: Nervous System
├── Severity: High
├── Impact: Interruzione flusso dati
└── Action: Tentativo riconnessione...
[Exception details with stack trace]
```

### 3. Progress Updates
```
[15:30:45] 🧬 DNA         │ Analisi pattern di mercato
[▰▰▰▰▰▰▰▰▰▰] 100% │ Pattern detection    │ ⏱️ 2.3s
[▰▰▰▰▰▰▰▰▰▰] 100% │ Strategy evolution   │ ⏱️ 1.8s
[▰▰▰▰▰▰▰▰▱▱]  80% │ Performance update   │ ⏱️ 3.1s
```

## Best Practices

### 1. Logging Levels
- DEBUG: Informazioni dettagliate per debugging
- INFO: Operazioni normali del sistema
- WARNING: Eventi inattesi ma non critici
- ERROR: Errori che richiedono attenzione
- CRITICAL: Errori che bloccano il sistema

### 2. Component Logging
- Usa il ComponentLogger per moduli specifici
- Mantieni consistenza nelle icone
- Log chiari e concisi
- Includi contesto rilevante

### 3. Progress Tracking
- Mostra sempre il progresso per operazioni lunghe
- Aggiorna regolarmente la progress bar
- Fornisci stime tempo rimanente
- Combina progress bar con log informativi

### 4. File Management
- Rotazione automatica dei log
- Compressione file storici
- Pulizia periodica
- Separazione per componente

### 5. Performance
- Buffering per log ad alta frequenza
- Livelli log appropriati
- Evita logging eccessivo
- Monitora dimensione file

## Testing

### 1. Unit Test
```python
def test_component_logger():
    logger = get_component_logger("dna")
    logger.info("Test message")
    assert True

def test_progress_logger():
    with get_progress_logger() as progress:
        task_id = progress.add_task("Test", total=100)
        progress.update(task_id, advance=50)
        assert True
```

### 2. Integration Test
```python
def test_full_workflow():
    # Setup
    logger = get_component_logger("dna")
    progress = get_progress_logger()
    
    # Workflow test
    with progress:
        task = progress.add_task("Analysis", total=100)
        for i in range(10):
            progress.update(task, advance=10)
            logger.info(f"Step {i+1} completed")
```

## CLI Integration

### 1. Progress Command
```python
@click.command()
@click.option("--show-progress", is_flag=True)
def process(show_progress):
    """Processa dati con progress bar"""
    if show_progress:
        with get_progress_logger() as progress:
            task = progress.add_task("Processing", total=100)
            # Process logic here
```

### 2. Logging Command
```python
@click.command()
@click.option("--component", type=str)
@click.option("--level", type=str)
def log(component, level):
    """Visualizza log per componente"""
    logger = get_component_logger(component)
    getattr(logger, level.lower())("Test message")
```

## Manutenzione

### 1. Log Rotation
- Configurazione in trace.yaml
- Rotazione automatica > 10MB
- Mantieni ultimi 5 file
- Comprimi file storici

### 2. Monitoring
- Controlla dimensione file
- Verifica livelli log
- Monitora performance
- Pulisci log obsoleti

### 3. Troubleshooting
- Verifica configurazione
- Controlla permessi file
- Monitora uso memoria
- Valida formato log
