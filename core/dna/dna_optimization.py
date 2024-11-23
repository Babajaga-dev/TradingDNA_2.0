"""DNA optimization module for strategy validation and optimization.

Questo modulo contiene la logica per la validazione e ottimizzazione delle strategie.
"""
import time
from typing import Dict
import logging
import numpy as np
import pandas as pd
from .dna_base import DNABase

logger = logging.getLogger(__name__)

class DNAOptimization(DNABase):
    """Gestisce la validazione e ottimizzazione delle strategie."""

    def validate_strategy(self, data: pd.DataFrame) -> Dict[str, float]:
        """Valida la strategia su un set di dati.
        
        Args:
            data: DataFrame con i dati OHLCV
            
        Returns:
            Dict[str, float]: Metriche di validazione
            
        Raises:
            ValueError: Se i dati non sono validi
        """
        logger.info("Avvio validazione strategia")
        
        # Validazione input rigorosa
        if data is None:
            raise ValueError("Dati di input nulli")
            
        if data.empty:
            raise ValueError("DataFrame vuoto")
            
        if len(data) < 2:
            raise ValueError("Dati insufficienti per validazione")
            
        # Controllo colonne richieste
        required_columns = ['close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        # Solleva eccezione se mancano colonne o se le colonne sono solo 'invalid'
        if missing_columns or (len(data.columns) == 1 and list(data.columns)[0] == 'invalid'):
            logger.error(f"Colonne mancanti o non valide: {data.columns}")
            raise ValueError(f"Colonne mancanti o non valide: {data.columns}")
        
        try:
            # Genera segnali con gestione errori
            signals = np.zeros(len(data))
            for i in range(len(data)):
                try:
                    signals[i] = self.get_strategy_signal(data.iloc[:i+1])
                except Exception as e:
                    logger.error(f"Errore nel calcolo segnale: {str(e)}")
                    signals[i] = 0
            
            # Calcola returns
            returns = data['close'].pct_change().values
            strategy_returns = signals[:-1] * returns[1:]  # Dimensione N-1
            
            # Calcola equity curve con gestione casi limite
            equity = np.cumprod(1 + strategy_returns) if len(strategy_returns) > 0 else np.array([1])
            
            # Calcola metriche con gestione eccezioni
            raw_return = equity[-1] - 1 if len(equity) > 0 else 0
            # Normalizza il return nell'intervallo [-1, 1] usando tanh
            total_return = np.tanh(raw_return)
            
            volatility = np.std(strategy_returns) * np.sqrt(252) if len(strategy_returns) > 1 else 0
            sharpe = (np.mean(strategy_returns) / (np.std(strategy_returns) + 1e-6) * np.sqrt(252)) if len(strategy_returns) > 1 else 0
            
            # Calcola drawdown e assicura che sia positivo
            drawdowns = 1 - equity / np.maximum.accumulate(equity)
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 1 else 0
            
            # Calcola statistiche trade
            trades = np.diff(signals) != 0  # Dimensione N-1
            num_trades = np.sum(trades)
            
            # Calcolo win rate corretto
            if num_trades > 0:
                # Usa gli stessi returns per trades e strategy_returns
                trade_returns = strategy_returns[trades]  # Filtra solo i returns dei trade
                win_rate = np.mean(trade_returns > 0) if len(trade_returns) > 0 else 0
            else:
                win_rate = 0
            
            metrics = {
                'total_return': total_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_drawdown,
                'num_trades': num_trades,
                'win_rate': win_rate
            }
            
            # Aggiorna le metriche direttamente
            self.strategy_metrics.total_return = total_return
            self.strategy_metrics.volatility = volatility
            self.strategy_metrics.sharpe_ratio = sharpe
            self.strategy_metrics.max_drawdown = max_drawdown
            self.strategy_metrics.num_trades = num_trades
            self.strategy_metrics.win_rate = win_rate
            
            # Salva stato dopo validazione
            self.save_state()
            
            logger.info(f"Validazione completata: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Errore nella validazione: {str(e)}")
            raise ValueError(f"Errore nella validazione: {str(e)}")
        
    def optimize_strategy(self, data: pd.DataFrame) -> None:
        """Ottimizza tutti i geni della strategia.
        
        Args:
            data: DataFrame con i dati OHLCV
        """
        logger.info("Avvio ottimizzazione strategia")
        
        # Validazione input
        if data is None or len(data) < 20:  # Minimo per split
            logger.warning("Dati insufficienti per ottimizzazione")
            return
        
        start_time = time.time()
        
        # Split dei dati
        train_size = max(int(len(data) * 0.7), 10)  # Assicura dimensione minima
        train_data = data.iloc[:train_size]
        test_data = data.iloc[train_size:]
        
        # Ottimizza ogni gene sul training set
        for gene in self.genes.values():
            try:
                gene.optimize_params(train_data)
            except Exception as e:
                logger.error(f"Errore nell'ottimizzazione del gene {gene.name}: {str(e)}")
            
        # Valida su test set
        test_metrics = self.validate_strategy(test_data)
        
        # Registra latenza
        latency = (time.time() - start_time) * 1000  # ms
        self.performance_metrics.record_execution_latency(latency)
        
        # Aggiorna metriche sistema
        self.performance_metrics.update_system_metrics()
        
        # Salva stato dopo ottimizzazione
        self.save_state()
        
        logger.info(f"Ottimizzazione completata, metriche test: {test_metrics}")