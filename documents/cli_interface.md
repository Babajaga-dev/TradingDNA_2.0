# CLI Interface

## Design Principles
- Interfaccia user-friendly
- Progress bars interattive
- Colori per stati diversi
- Layout organizzato e chiaro

## Funzioni Principali Dashboard

### 1. Download Dati Storici
```python
def download_historical_data():
    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading historical data...", total=100)
        # Download logic
        progress.update(task, advance=1)
```
Output:
```
Downloading Historical Data [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── BTC/USDT    [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── ETH/USDT    [━━━━━━━━━━━━━━━━━━━━━━] 100%
└── Data Validation [━━━━━━━━━━━━━━━━━━━━━━] 100%
```

### 2. Training
```python
def train_system():
    with Progress() as progress:
        task = progress.add_task("[green]Training system...", total=100)
        # Training logic
        progress.update(task, advance=1)
```
Output:
```
System Training [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── Data Preprocessing [━━━━━━━━━━━━━━━━] 100%
├── Strategy Evolution [━━━━━━━━━━━━━━━━] 100%
└── Parameter Optimization [━━━━━━━━━━━━] 100%
```

### 3. Backtest
```python
def run_backtest():
    with Progress() as progress:
        task = progress.add_task("[yellow]Running backtest...", total=100)
        # Backtest logic
        progress.update(task, advance=1)
```
Output:
```
Backtest Progress [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── Strategy Testing [━━━━━━━━━━━━━━━━━━] 100%
├── Performance Analysis [━━━━━━━━━━━━━━] 100%
└── Report Generation [━━━━━━━━━━━━━━━━━] 100%
```

### 4. Paper Trading
```python
def start_paper_trading():
    with Live() as live:
        table = Table()
        table.add_column("Asset")
        table.add_column("Position")
        table.add_column("P/L")
        # Paper trading logic
```
Output:
```
Paper Trading Active
├── Account Balance: $10,000
├── Open Positions: 2
└── Current P/L: +$150
```

### 5. Live Trading
```python
def start_live_trading():
    with Live() as live:
        table = Table()
        table.add_column("Status")
        table.add_column("Performance")
        table.add_column("Risk")
        # Live trading logic
```
Output:
```
Live Trading Active
├── System Health: ✅
├── Risk Level: Low
└── Active Trades: 3
```

### 6. Reset Logs
```python
def reset_logs():
    with Progress() as progress:
        task = progress.add_task("[magenta]Resetting logs...", total=100)
        # Reset logic
        progress.update(task, advance=1)
```
Output:
```
Log Reset Progress [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── Archiving Old Logs [━━━━━━━━━━━━━━━━━] 100%
├── Cleaning Files [━━━━━━━━━━━━━━━━━━━━━] 100%
└── Initializing New Logs [━━━━━━━━━━━━━━] 100%
```

### 7. Reset System
```python
def reset_system():
    with Progress() as progress:
        task = progress.add_task("[red]Resetting system...", total=100)
        # Reset logic
        progress.update(task, advance=1)
```
Output:
```
System Reset Progress [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── Database Cleanup [━━━━━━━━━━━━━━━━━━━━━] 100%
├── Config Reset [━━━━━━━━━━━━━━━━━━━━━━━━] 100%
└── System Initialization [━━━━━━━━━━━━━━━━] 100%
```

### 8. Exit
```python
def exit_system():
    with Progress() as progress:
        task = progress.add_task("[white]Shutting down...", total=100)
        # Shutdown logic
        progress.update(task, advance=1)
```
Output:
```
Shutdown Progress [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── Saving State [━━━━━━━━━━━━━━━━━━━━━━] 100%
├── Closing Connections [━━━━━━━━━━━━━━━━] 100%
└── Backup Complete [━━━━━━━━━━━━━━━━━━━] 100%
```

## Menu Interface
```python
def show_menu():
    console.print("[bold cyan]TradingDNA 2.0 Dashboard[/]")
    console.print("1. Download Historical Data")
    console.print("2. Training")
    console.print("3. Backtest")
    console.print("4. Paper Trading")
    console.print("5. Live Trading")
    console.print("6. Reset Logs")
    console.print("7. Reset System")
    console.print("8. Exit")
```

## Progress Indicators
Ogni funzione include:
- Progress bar dettagliata
- Status updates in tempo reale
- Indicatori colorati
- Metriche rilevanti

## Error Handling
```python
try:
    # Operation logic
except Exception as e:
    console.print(f"[red]Error: {str(e)}[/]")
    console.print_exception()
