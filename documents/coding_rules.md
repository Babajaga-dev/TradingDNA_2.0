# Coding Rules

## 1. Limiti Strutturali

### File
- Massimo 400 righe di codice per file
- Un modulo/classe per file
- Nome file descrittivo in snake_case
- Estensione .py per Python, .yaml per configurazioni

### Directory
- Massimo 2 livelli di profondità
- Nomi directory in lowercase
- Nomi significativi e descrittivi
- Separazione chiara per funzionalità

## 2. Configurazione

### Parametri
- Nessun valore hardcoded nel codice
- Tutti i parametri in file YAML
- Configurazione per modulo
- Valori default documentati

### Gestione
- Uso obbligatorio ConfigManager
- Accesso tramite interfacce
- Validazione parametri
- Cache configurazioni

## 3. Logging

### Organizzazione
- Logger indipendente per modulo
- File log separati
- Configurazione granulare
- Rotazione automatica

### Messaggi
- Chiari e descrittivi
- Livello appropriato (DEBUG, INFO, etc.)
- Informazioni contestuali
- Timestamp obbligatorio

## 4. Codice

### Documentazione
```python
def process_data(data: Dict[str, Any]) -> List[float]:
    """
    Processa i dati di mercato applicando filtri e normalizzazione.

    Args:
        data: Dictionary contenente i dati grezzi
            - prices: List[float] serie prezzi
            - volume: List[float] serie volumi
            
    Returns:
        List[float]: Dati processati e normalizzati
        
    Raises:
        ValueError: Se i dati sono invalidi
        ProcessingError: Se il processing fallisce
    """
    pass
```

### Type Hints
- Obbligatori per parametri
- Obbligatori per return value
- Uso di typing per strutture complesse
- Documentazione tipi custom

### Naming
- Variabili: snake_case descrittive
- Classi: PascalCase
- Costanti: UPPERCASE_WITH_UNDERSCORE
- Funzioni: verbo_oggetto (es. process_data)

### Testing
- Test unitari obbligatori
- Coverage minimo 80%
- Mock per dipendenze esterne
- Test integrazione per componenti chiave

## 5. Git

### Commit
- Atomici (una feature/fix per commit)
- Messaggi descrittivi
- Riferimento issue/ticket
- No commit su master diretto

### Branch
- Feature branch per sviluppo
- Nome branch descrittivo
- Merge solo dopo review
- Squash commit al merge

## 6. Best Practices

### SOLID
- Single Responsibility
- Open/Closed
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

### Clean Code
- Funzioni piccole e focalizzate
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple)
- Composizione over ereditarietà

### Performance
- Profiling code critico
- Ottimizzazione memory usage
- Caching dove appropriato
- Async per I/O bound

### Sicurezza
- Validazione input
- Sanitizzazione dati
- Gestione errori robusta
- Logging sicuro (no dati sensibili)
