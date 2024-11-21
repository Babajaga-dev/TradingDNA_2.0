"""DNA Data Downloader Module.

Questo modulo gestisce il download dei dati di mercato e la loro suddivisione
in insiemi di training, validation e backtesting.
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
from rich.table import Table
from rich.console import Console

from core.exceptions import DNADataError
from core.base_exchange import BaseExchange
from utils.logger import get_component_logger, get_progress_logger
from utils.config import load_config, ConfigError

# Logger componente DNA
logger = get_component_logger("DNA")

@dataclass
class DatasetConfig:
    """Configurazione per il download e la suddivisione dei dati."""
    training_ratio: float = 0.7
    validation_ratio: float = 0.15
    testing_ratio: float = 0.15
    
    def __post_init__(self) -> None:
        """Validazione dei ratio."""
        total = self.training_ratio + self.validation_ratio + self.testing_ratio
        if not 0.99 < total < 1.01:
            raise DNADataError(f"I ratio devono sommare a 1.0, trovato: {total}")

class DNADataDownloader:
    """Gestisce il download e la preparazione dei dati per il DNA system."""
    
    def __init__(self, exchange: BaseExchange):
        """Inizializza il downloader.
        
        Args:
            exchange: Istanza di BaseExchange per il download
            
        Raises:
            ConfigError: Se ci sono errori nel caricamento della configurazione
        """
        self.exchange = exchange
        try:
            self.config = load_config("dna.yaml")
            self.dataset_config = DatasetConfig(
                training_ratio=self.config["data"]["split_ratios"]["training"],
                validation_ratio=self.config["data"]["split_ratios"]["validation"],
                testing_ratio=self.config["data"]["split_ratios"]["testing"]
            )
        except Exception as e:
            raise ConfigError(f"Errore caricamento configurazione DNA: {str(e)}")
        
    def download_candles(
        self, 
        symbol: str,
        timeframes: List[str],
        num_candles: int
    ) -> Dict[str, pd.DataFrame]:
        """Scarica le candele per i timeframe specificati.
        
        Args:
            symbol: Simbolo trading (es. BTC/USDT)
            timeframes: Lista di timeframe (es. ["1h", "4h", "1d"])
            num_candles: Numero totale di candele da scaricare
            
        Returns:
            Dict con chiave timeframe e valore DataFrame delle candele
        
        Raises:
            DNADataError: Se il download fallisce
        """
        results = {}
        
        # Inizializza progress logger
        with get_progress_logger() as progress:
            task_id = progress.add_task(
                f"[bold blue]Download {symbol}",
                total=len(timeframes)
            )
            
            for tf in timeframes:
                try:
                    logger.info(f"Download {num_candles} candele {symbol} {tf}")
                    candles = self.exchange.fetch_ohlcv(
                        symbol=symbol,
                        timeframe=tf,
                        limit=num_candles
                    )
                    
                    df = pd.DataFrame(
                        candles,
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    )
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    
                    results[tf] = df
                    progress.update(task_id, advance=1)
                    logger.info(f"Completato download {symbol} {tf}")
                    
                except Exception as e:
                    logger.error(f"Errore download {symbol} {tf}: {str(e)}")
                    raise DNADataError(f"Errore download {symbol} {tf}: {str(e)}")
                    
        return results
    
    def validate_data(self, data: Dict[str, pd.DataFrame]) -> None:
        """Valida i dati scaricati.
        
        Args:
            data: Dict con chiave timeframe e valore DataFrame
            
        Raises:
            DNADataError: Se la validazione fallisce
        """
        logger.info("Inizio validazione dati")
        
        for tf, df in data.items():
            try:
                # Verifica colonne
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    raise DNADataError(f"Colonne mancanti in {tf}: {missing_cols}")
                
                # Verifica dati mancanti
                if df.isnull().any().any():
                    raise DNADataError(f"Trovati dati mancanti in {tf}")
                
                # Verifica ordine timestamp
                if not df.index.is_monotonic_increasing:
                    raise DNADataError(f"Timestamp non ordinati in {tf}")
                    
                logger.info(f"Validazione dati {tf} completata")
                
            except Exception as e:
                logger.error(f"Errore validazione {tf}: {str(e)}")
                raise DNADataError(f"Errore validazione {tf}: {str(e)}")
    
    def split_data(
        self,
        data: Dict[str, pd.DataFrame]
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
        """Divide i dati in training, validation e testing.
        
        Args:
            data: Dict con chiave timeframe e valore DataFrame
            
        Returns:
            Tuple di (training_data, validation_data, testing_data)
        """
        logger.info("Inizio split dei dati")
        
        training = {}
        validation = {}
        testing = {}
        
        for tf, df in data.items():
            total_rows = len(df)
            
            # Calcola gli indici di split
            train_idx = int(total_rows * self.dataset_config.training_ratio)
            val_idx = train_idx + int(total_rows * self.dataset_config.validation_ratio)
            
            # Split dei dati
            training[tf] = df.iloc[:train_idx]
            validation[tf] = df.iloc[train_idx:val_idx]
            testing[tf] = df.iloc[val_idx:]
            
            logger.info(
                f"Split {tf}: "
                f"training={len(training[tf])} "
                f"validation={len(validation[tf])} "
                f"testing={len(testing[tf])}"
            )
            
        return training, validation, testing
    
    def save_data(
        self,
        training: Dict[str, pd.DataFrame],
        validation: Dict[str, pd.DataFrame],
        testing: Dict[str, pd.DataFrame],
        symbol: str
    ) -> None:
        """Salva i dataset su file.
        
        Args:
            training: Dict training data
            validation: Dict validation data 
            testing: Dict testing data
            symbol: Simbolo trading
        """
        logger.info("Inizio salvataggio dati")
        
        base_path = self.config["data"]["base_path"]
        symbol_safe = symbol.replace("/", "_")
        
        datasets = {
            "training": training,
            "validation": validation,
            "testing": testing
        }
        
        # Inizializza progress logger
        with get_progress_logger() as progress:
            total_files = len(datasets) * sum(len(d) for d in datasets.values())
            task_id = progress.add_task(
                "[bold blue]Salvataggio dati",
                total=total_files
            )
            
            for name, data in datasets.items():
                for tf, df in data.items():
                    try:
                        filename = f"{base_path}/{symbol_safe}_{tf}_{name}.parquet"
                        df.to_parquet(filename)
                        logger.info(f"Salvato {name} dataset per {symbol} {tf}")
                        progress.update(task_id, advance=1)
                        
                    except Exception as e:
                        logger.error(f"Errore salvataggio {name} {tf}: {str(e)}")
                        raise DNADataError(f"Errore salvataggio {name} {tf}: {str(e)}")

    def display_data(self, symbol: str, timeframe: str, dataset_type: str = None) -> None:
        """Visualizza i dati scaricati per un simbolo e timeframe specifico.
        
        Args:
            symbol: Simbolo trading (es. BTC/USDT)
            timeframe: Timeframe da visualizzare
            dataset_type: Tipo di dataset (training/validation/testing/None per tutti)
        """
        console = Console()
        base_path = self.config["data"]["base_path"]
        symbol_safe = symbol.replace("/", "_")
        
        # Crea tabella per il riepilogo
        summary_table = Table(title=f"📊 Riepilogo Dati {symbol} {timeframe}")
        summary_table.add_column("Dataset", style="cyan")
        summary_table.add_column("Candele", justify="right", style="green")
        summary_table.add_column("Prima Data", style="yellow")
        summary_table.add_column("Ultima Data", style="yellow")
        summary_table.add_column("Close Min", justify="right", style="red")
        summary_table.add_column("Close Max", justify="right", style="green")
        summary_table.add_column("Close Media", justify="right", style="blue")
        summary_table.add_column("Volume Medio", justify="right", style="magenta")
        
        datasets = ["training", "validation", "testing"] if not dataset_type else [dataset_type]
        
        for ds in datasets:
            try:
                filename = f"{base_path}/{symbol_safe}_{timeframe}_{ds}.parquet"
                df = pd.read_parquet(filename)
                
                summary_table.add_row(
                    ds,
                    str(len(df)),
                    df.index[0].strftime("%Y-%m-%d %H:%M"),
                    df.index[-1].strftime("%Y-%m-%d %H:%M"),
                    f"{df['close'].min():.2f}",
                    f"{df['close'].max():.2f}",
                    f"{df['close'].mean():.2f}",
                    f"{df['volume'].mean():.0f}"
                )
                
            except Exception as e:
                logger.error(f"Errore lettura dati {ds}: {str(e)}")
                continue
        
        console.print("\n")
        console.print(summary_table)
        
        # Se richiesto un dataset specifico, mostra anche i dati dettagliati
        if dataset_type:
            try:
                filename = f"{base_path}/{symbol_safe}_{timeframe}_{dataset_type}.parquet"
                df = pd.read_parquet(filename)
                
                detail_table = Table(title=f"📈 Dettaglio {dataset_type}")
                detail_table.add_column("Data", style="yellow")
                detail_table.add_column("Open", justify="right", style="green")
                detail_table.add_column("High", justify="right", style="green")
                detail_table.add_column("Low", justify="right", style="red")
                detail_table.add_column("Close", justify="right", style="blue")
                detail_table.add_column("Volume", justify="right", style="magenta")
                
                # Mostra le prime e ultime 5 righe
                rows_to_show = pd.concat([df.head(5), df.tail(5)])
                for idx, row in rows_to_show.iterrows():
                    detail_table.add_row(
                        idx.strftime("%Y-%m-%d %H:%M"),
                        f"{row['open']:.2f}",
                        f"{row['high']:.2f}",
                        f"{row['low']:.2f}",
                        f"{row['close']:.2f}",
                        f"{row['volume']:.0f}"
                    )
                    if len(detail_table.rows) == 5:
                        detail_table.add_row("...", "...", "...", "...", "...", "...")
                
                console.print("\n")
                console.print(detail_table)
                
            except Exception as e:
                logger.error(f"Errore lettura dati dettagliati: {str(e)}")
