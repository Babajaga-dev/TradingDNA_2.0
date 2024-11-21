# Menu Interattivo

Il comando `python main.py menu` fornisce un'interfaccia interattiva per eseguire le operazioni del sistema in modo guidato e sequenziale.

## Sequenza Operativa

### 1. Inizializzazione Sistema
```bash
python main.py menu
> 1. Inizializzazione Sistema
```
Questa operazione:
- Crea le directory necessarie
- Inizializza i file di configurazione
- Prepara l'ambiente di logging
- Verifica le dipendenze

### 2. Configurazione
```bash
> 2. Gestione Configurazione
```
Permette di:
- Visualizzare la configurazione attuale
- Modificare parametri
- Ripristinare configurazione default
- Validare configurazione

### 3. Download Dati
```bash
> 3. Download Dati
```
Operazioni disponibili:
- Download dati storici
- Selezione timeframe
- Selezione coppie trading
- Verifica integrità dati

### 4. Analisi Pattern
```bash
> 4. Sistema DNA
```
Funzionalità:
- Inizializzazione DNA
- Analisi pattern su timeframe
- Visualizzazione scoring
- Export pattern trovati

### 5. Metriche
```bash
> 5. Visualizza Metriche
```
Mostra:
- Metriche di sistema
- Metriche di performance
- Statistiche pattern
- Health score

## Workflow Consigliato

1. **Setup Iniziale**
   ```bash
   python main.py menu
   > 1. Inizializzazione Sistema
   ```
   Eseguire al primo utilizzo o dopo aggiornamenti

2. **Configurazione Base**
   ```bash
   > 2. Gestione Configurazione
   > 2.1 Visualizza Configurazione
   > 2.2 Modifica Parametri
   ```
   Verificare e personalizzare i parametri principali

3. **Preparazione Dati**
   ```bash
   > 3. Download Dati
   > 3.1 Download BTC/USDT 1h
   > 3.2 Verifica Integrità
   ```
   Scaricare i dati necessari per l'analisi

4. **Analisi Tecnica**
   ```bash
   > 4. Sistema DNA
   > 4.1 Inizializza DNA
   > 4.2 Analizza Pattern
   ```
   Eseguire l'analisi pattern sui dati

5. **Monitoraggio**
   ```bash
   > 5. Visualizza Metriche
   > 5.1 Metriche Sistema
   > 5.2 Performance Pattern
   ```
   Verificare le performance del sistema

## Comandi Rapidi

Per utenti esperti, è possibile eseguire le operazioni direttamente da CLI:

```bash
# Workflow completo
python main.py init
python main.py config show
python main.py download market --pair BTC/USDT --timeframe 1h
python main.py dna analyze --pair BTC/USDT --timeframe 1h
python main.py metrics show
```

## Note Importanti

1. **Ordine Operazioni**
   - Rispettare la sequenza delle operazioni
   - Non saltare passaggi fondamentali
   - Verificare il successo di ogni operazione

2. **Validazione**
   - Controllare i log dopo ogni operazione
   - Verificare l'integrità dei dati
   - Monitorare le metriche di sistema

3. **Backup**
   - Eseguire backup regolari della configurazione
   - Salvare i pattern identificati
   - Mantenere log delle operazioni

4. **Troubleshooting**
   - Consultare i log in caso di errori
   - Verificare lo stato del sistema
   - Utilizzare i comandi di diagnostica
