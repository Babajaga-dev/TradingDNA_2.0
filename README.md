# TradingDNA 2.0

TradingDNA 2.0 è un sistema di trading algoritmico biologico che implementa vari sottosistemi ispirati alla biologia per l'analisi e l'esecuzione di strategie di trading.

## Documentazione

La documentazione completa del sistema è organizzata nei seguenti capitoli:

1. [Installazione e Inizializzazione](manual/01_installation.md)
   - Setup del sistema
   - Inizializzazione componenti
   - Verifica installazione

2. [Configurazione](manual/02_configuration.md)
   - File di configurazione
   - Parametri configurabili
   - Gestione via CLI

3. [Interfaccia CLI](manual/03_cli_interface.md)
   - Gestione log
   - Download dati
   - Comandi disponibili
   - Opzioni globali

4. [Sistema DNA](manual/04_dna_system.md)
   - Pattern Recognition
   - Metriche DNA
   - Health Score
   - Strategy Fitness

5. [Gestione Dati](manual/05_data_management.md)
   - Struttura dati
   - Formati supportati
   - Download e validazione
   - Backup e ripristino

6. [Sistema di Metriche](manual/06_metrics_system.md)
   - Metriche di performance
   - Metriche di trading
   - Calcolo indicatori
   - Monitoraggio sistema

7. [Altri Sistemi](manual/07_other_systems.md)
   - Sistema Immunitario
   - Sistema Metabolico
   - Sistema Nervoso
   - Sistema Endocrino
   - Sistema Riproduttivo

8. [Menu Interattivo](manual/08_interactive_menu.md)
   - Workflow operativo
   - Sequenza comandi
   - Operazioni guidate
   - Best practices

## Quick Start

```bash
# Avvia menu interattivo
python main.py menu

# Oppure esegui i comandi singolarmente:

# 1. Inizializza il sistema
python main.py init

# 2. Scarica dati di mercato
python main.py download market --pair BTC/USDT --timeframe 1h

# 3. Avvia analisi pattern
python main.py dna analyze --pair BTC/USDT --timeframe 1h

# 4. Visualizza metriche
python main.py metrics show
```

## Workflow Consigliato

1. Utilizzare il menu interattivo (`python main.py menu`) per essere guidati attraverso le operazioni necessarie
2. Seguire la sequenza operativa consigliata nella [documentazione del menu](manual/08_interactive_menu.md)
3. Consultare i capitoli specifici della documentazione per approfondimenti

## Supporto

Per problemi, suggerimenti o contributi:
1. Consulta la documentazione dettagliata nella cartella `manual/`
2. Verifica i log in `logs/`
3. Usa il comando `python main.py help` per aiuto sui comandi
