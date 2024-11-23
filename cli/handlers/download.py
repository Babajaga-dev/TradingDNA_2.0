"""
Handler per il Download dei Dati
"""
import os
import yaml
from typing import List, Dict
from pathlib import Path

from cli.utils import console, create_progress, print_error, print_success
from core.base_exchange import BaseExchange
from core.dna_downloader import DNADataDownloader
from core.exceptions import ConfigurationError, AuthenticationError, DNADataError
from utils.logger_base import get_component_logger

# Setup logger
logger = get_component_logger('CLI.Download')

def get_dataset_config(config: dict, dataset_name: str, pair: str = None, timeframe: str = None) -> List[Dict]:
    """Estrae la configurazione del dataset specificato"""
    dataset = config['data'].get(dataset_name)
    if not dataset:
        return []
    
    pairs = dataset['pairs']
    if pair:
        pairs = [p for p in pairs if p['symbol'] == pair]
    
    result = []
    for p in pairs:
        timeframes = [timeframe] if timeframe else p['timeframes']
        for tf in timeframes:
            if tf in p['timeframes']:  # Verifica che il timeframe sia supportato
                result.append({
                    'symbol': p['symbol'],
                    'timeframe': tf,
                    'candles': p['candles']  # Usa il numero di candele invece delle date
                })
    return result

def handle_download(args):
    """Gestisce il comando download"""
    logger.debug("Avvio download dati")
    try:
        # Carica la configurazione DNA
        with open('config/dna.yaml', 'r') as f:
            config = yaml.safe_load(f)
            
        # Crea le directory necessarie
        data_path = config['data']['base_path']
        os.makedirs(data_path, exist_ok=True)
        logger.debug(f"Directory dati creata: {data_path}")
        
        # Inizializza l'exchange
        exchange = BaseExchange("config/network.yaml")
        downloader = DNADataDownloader(exchange)
        logger.debug("Exchange inizializzato")

        # Determina quali dataset scaricare
        datasets = ['training', 'testing', 'paper_trading'] if args.dataset == 'all' else [args.dataset]
        logger.debug(f"Dataset da scaricare: {datasets}")
        
        # Raccoglie tutte le serie da scaricare
        all_series = []
        for dataset_name in datasets:
            series = get_dataset_config(config, dataset_name, args.pair, args.timeframe)
            for s in series:
                s['dataset'] = dataset_name
            all_series.extend(series)

        if not all_series:
            logger.warning("Nessuna serie temporale trovata")
            print_error("Nessuna serie temporale trovata per i criteri specificati")
            return

        with create_progress() as progress:
            # Task per il progresso totale
            total_task = progress.add_task(
                "[cyan]Download totale", 
                total=len(all_series)
            )
            
            # Task per le operazioni
            operation_task = progress.add_task(
                "[cyan]Operazione corrente",
                total=100,  # Usiamo percentuale per operazioni
                visible=False
            )

            # Per ogni serie temporale
            for series in all_series:
                symbol_desc = f"{series['symbol']} ({series['timeframe']}) - {series['dataset']}"
                console.print(f"\n[cyan]Elaborazione {symbol_desc}")
                logger.debug(f"Inizio elaborazione {symbol_desc}")
                
                try:
                    # Download (30% del progresso)
                    progress.update(operation_task, 
                                  visible=True, 
                                  description="[cyan]Download dati",
                                  completed=0)
                    
                    data = downloader.download_candles(
                        symbol=series['symbol'],
                        timeframes=[series['timeframe']],
                        num_candles=series['candles'],
                        progress=progress,
                        task_id=operation_task
                    )
                    progress.update(operation_task, completed=30)
                    logger.debug(f"Download completato: {len(data)} candele")
                    
                    # Validazione (20% del progresso)
                    progress.update(operation_task, 
                                  description="[cyan]Validazione dati",
                                  completed=30)
                    
                    downloader.validate_data(data)
                    progress.update(operation_task, completed=50)
                    logger.debug("Validazione completata")
                    
                    # Split (20% del progresso)
                    progress.update(operation_task, 
                                  description="[cyan]Split dataset",
                                  completed=50)
                    
                    training, validation, testing = downloader.split_data(data)
                    progress.update(operation_task, completed=70)
                    logger.debug("Split dataset completato")
                    
                    # Salvataggio (30% del progresso)
                    progress.update(operation_task, 
                                  description="[cyan]Salvataggio dati",
                                  completed=70)
                    
                    downloader.save_data(
                        training, validation, testing, 
                        series['symbol'],
                        progress=progress,
                        task_id=operation_task
                    )
                    progress.update(operation_task, completed=100)
                    logger.debug("Salvataggio completato")
                    
                    # Aggiorna progresso totale e resetta operazione
                    progress.update(total_task, advance=1)
                    progress.update(operation_task, visible=False, completed=0)
                    
                    # Calcola i giorni corrispondenti
                    days = downloader._calculate_days_from_candles(
                        series['timeframe'], 
                        series['candles']
                    )
                    
                    # Mostra info sul completamento
                    print_success(f"{symbol_desc} completato")
                    console.print(f"   Candele scaricate: {series['candles']} (giorni: {days:.1f})")
                    logger.debug(f"{symbol_desc} completato - Candele: {series['candles']}, Giorni: {days:.1f}")
                    
                except DNADataError as e:
                    logger.error(f"Errore durante il download di {series['symbol']}: {str(e)}")
                    print_error(f"Errore durante il download di {series['symbol']}: {str(e)}")
                    continue
                
    except (ConfigurationError, AuthenticationError) as e:
        logger.error(f"Errore di configurazione: {str(e)}")
        print_error(f"Errore di configurazione: {str(e)}")
    except Exception as e:
        logger.error(f"Errore inaspettato: {str(e)}")
        print_error(f"Errore inaspettato: {str(e)}")
