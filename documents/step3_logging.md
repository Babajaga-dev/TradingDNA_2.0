# Step 3: Sistema di Logging

## Obiettivi
1. Logger indipendenti per modulo
2. Configurazione granulare
3. Visualizzazione avanzata
4. Integrazione con CLI

## Implementazione Visuale

### 1. Formattazione Base
```python
from rich.console import Console
from rich.theme import Theme
from rich.logging import RichHandler
import logging

custom_theme = Theme({
    'info': 'cyan',
    'warning': 'yellow',
    'error': 'red bold',
    'critical': 'red bold reverse',
    'success': 'green bold'
})

console = Console(theme=custom_theme)
```

### 2. Handler Personalizzati
```python
class VisualLogHandler(RichHandler):
    def __init__(self):
        super().__init__(
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            show_time=True,
            show_path=False
        )
        
    def emit(self, record):
        # Aggiunge emoji based on level
        level_icons = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨',
            'SUCCESS': '✅'
        }
        record.icon = level_icons.get(record.levelname, '•')
        super().emit(record)
```

### 3. Progress Logging
```python
class ProgressLogger:
    def __init__(self, console):
        self.console = console
        
    def log_progress(self, task_name, current, total):
        percentage = (current / total) * 100
        bar_width = 50
        filled = int(bar_width * current / total)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        self.console.print(
            f"{task_name:<20} [{bar}] {percentage:>5.1f}%"
        )
```

### 4. Component Status
```python
class ComponentLogger:
    def __init__(self, component_name):
        self.name = component_name
        self.icons = {
            'DNA': '🧬',
            'IMMUNE': '🛡️',
            'METABOLISM': '⚡',
            'NERVOUS': '🧠',
            'ENDOCRINE': '⚖️',
            'REPRODUCTIVE': '🔄'
        }
        
    def log(self, message, level='INFO'):
        icon = self.icons.get(self.name, '•')
        console.print(
            f"{icon} {self.name:<12} │ {message}",
            style=level.lower()
        )
```

## Configurazione YAML

```yaml
logging:
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
      format: "{icon} {time} │ {message}"
    
    immune:
      icon: "🛡️"
      color: "green"
      format: "{icon} {time} │ {message}"
    
    metabolism:
      icon: "⚡"
      color: "yellow"
      format: "{icon} {time} │ {message}"
```

## Esempi di Output

### 1. Status Update
```
🧬 DNA        │ 15:30:45 │ Analyzing market patterns...
├── Pattern Detection   [━━━━━━━━━━━━━━━━━━━━━] 100%
├── Strategy Evolution  [━━━━━━━━━━━━━━━━━━━━━] 100%
└── Performance Update [━━━━━━━━━━━━━━━━━    ] 85%
```

### 2. System Health
```
System Status Update
├── 🧬 DNA        │ Health: 98% │ [green]Optimal
├── 🛡️ Immune     │ Health: 95% │ [green]Protected
├── ⚡ Metabolism │ Health: 92% │ [yellow]Adapting
├── 🧠 Nervous    │ Health: 97% │ [green]Active
├── ⚖️ Endocrine  │ Health: 94% │ [green]Balanced
└── 🔄 Reproduce  │ Health: 91% │ [yellow]Evolving
```

### 3. Error Handling
```
❌ ERROR    │ 15:31:23 │ Connection lost to exchange
├── Component: Nervous System
├── Severity: High
├── Impact: Data Stream Interrupted
└── Action: Attempting reconnection...
[Exception details with stack trace]
```

## Integrazione CLI

### 1. Live Updates
```python
from rich.live import Live
from rich.table import Table

def show_live_logs():
    table = Table()
    table.add_column("Time")
    table.add_column("Component")
    table.add_column("Message")
    
    with Live(table, refresh_per_second=4):
        while True:
            # Update with new logs
            table.add_row("15:30:45", "🧬 DNA", "Pattern detected")
```

### 2. Interactive Filtering
```python
def filter_logs(component=None, level=None):
    """
    Filtra i log per componente e livello
    con visualizzazione interattiva
    """
    pass
```

## Best Practices

1. **Visualizzazione**
   - Usa colori consistenti
   - Mantieni layout pulito
   - Aggiungi progress bars
   - Usa icone intuitive

2. **Performance**
   - Buffering per high-frequency logs
   - Rotazione file automatica
   - Compressione logs storici
   - Pulizia automatica

3. **Usabilità**
   - Filtri interattivi
   - Search functionality
   - Export options
   - Real-time updates
