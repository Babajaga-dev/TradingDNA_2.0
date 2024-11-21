"""
Metriche per le strategie di trading
"""
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import pandas as pd

from utils.logger import get_component_logger

# Setup logger
logger = get_component_logger('Metrics.Strategy')

@dataclass
class StrategyMetrics:
    """Metriche di performance per una strategia."""
    # Metriche di rendimento
    total_return: float = 0.0
    annual_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    
    # Metriche di rischio
    max_drawdown: float = 0.0
    avg_drawdown: float = 0.0
    drawdown_duration: float = 0.0
    var_95: float = 0.0  # Value at Risk 95%
    
    # Metriche operative
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_trade: float = 0.0
    num_trades: int = 0
    
    # Metriche di qualità
    strategy_fitness: float = 0.0
    market_correlation: float = 0.0
    alpha: float = 0.0
    beta: float = 0.0
    
    def calculate_returns_metrics(self, equity_curve: np.ndarray) -> None:
        """Calcola le metriche basate sui rendimenti."""
        if len(equity_curve) < 2:
            logger.warning("Serie storica troppo corta per calcolare le metriche")
            return
            
        # Calcola rendimenti
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        # Rendimento totale e annualizzato
        self.total_return = (equity_curve[-1] / equity_curve[0]) - 1
        self.annual_return = (1 + self.total_return) ** (252 / len(returns)) - 1
        
        # Volatilità
        self.volatility = np.std(returns) * np.sqrt(252)
        
        # Sharpe e Sortino ratio
        risk_free_rate = 0.02  # TODO: Rendere configurabile
        excess_returns = returns - risk_free_rate/252
        
        if self.volatility > 0:
            self.sharpe_ratio = np.mean(excess_returns) / self.volatility
            
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_vol = np.std(downside_returns) * np.sqrt(252)
            self.sortino_ratio = np.mean(excess_returns) / downside_vol
            
        logger.debug(f"Calcolate metriche rendimenti: return={self.total_return:.4f}, "
                    f"sharpe={self.sharpe_ratio:.4f}")
                    
    def calculate_risk_metrics(self, equity_curve: np.ndarray) -> None:
        """Calcola le metriche di rischio."""
        if len(equity_curve) < 2:
            return
            
        # Calcola drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        
        self.max_drawdown = np.min(drawdown)
        self.avg_drawdown = np.mean(drawdown[drawdown < 0])
        
        # Calcola durata drawdown
        underwater = drawdown < 0
        underwater_periods = np.diff(underwater.astype(int))
        if len(underwater_periods) > 0:
            self.drawdown_duration = np.mean(underwater_periods == -1)
            
        # Calcola VaR
        returns = np.diff(equity_curve) / equity_curve[:-1]
        self.var_95 = np.percentile(returns, 5)
        
        logger.debug(f"Calcolate metriche rischio: max_dd={self.max_drawdown:.4f}, "
                    f"var95={self.var_95:.4f}")
                    
    def calculate_trade_metrics(self, trades: List[Dict]) -> None:
        """Calcola le metriche operative basate sui trade."""
        if not trades:
            return
            
        self.num_trades = len(trades)
        profits = [t['profit'] for t in trades]
        
        winning_trades = [p for p in profits if p > 0]
        if self.num_trades > 0:
            self.win_rate = len(winning_trades) / self.num_trades
            
        total_profit = sum(p for p in profits if p > 0)
        total_loss = abs(sum(p for p in profits if p < 0))
        
        if total_loss > 0:
            self.profit_factor = total_profit / total_loss
            
        self.avg_trade = np.mean(profits)
        
        logger.debug(f"Calcolate metriche trade: win_rate={self.win_rate:.4f}, "
                    f"profit_factor={self.profit_factor:.4f}")
                    
    def calculate_quality_metrics(self, strategy_returns: np.ndarray, 
                                market_returns: np.ndarray) -> None:
        """Calcola le metriche di qualità della strategia."""
        if len(strategy_returns) != len(market_returns):
            logger.error("Serie storiche di lunghezza diversa")
            return
            
        # Calcola correlazione con il mercato
        self.market_correlation = np.corrcoef(strategy_returns, market_returns)[0,1]
        
        # Calcola alpha e beta
        market_var = np.var(market_returns)
        if market_var > 0:
            self.beta = np.cov(strategy_returns, market_returns)[0,1] / market_var
            self.alpha = np.mean(strategy_returns) - self.beta * np.mean(market_returns)
            
        # Calcola fitness complessivo
        weights = {
            'sharpe_ratio': 0.2,
            'sortino_ratio': 0.2,
            'profit_factor': 0.2,
            'win_rate': 0.15,
            'max_drawdown': 0.15,
            'market_correlation': 0.1
        }
        
        # Normalizza le metriche
        normalized = {
            'sharpe_ratio': max(min(self.sharpe_ratio / 2, 1), 0),
            'sortino_ratio': max(min(self.sortino_ratio / 2, 1), 0),
            'profit_factor': max(min(self.profit_factor / 3, 1), 0),
            'win_rate': self.win_rate,
            'max_drawdown': max(min(-self.max_drawdown / 0.2, 1), 0),
            'market_correlation': max(min((1 - abs(self.market_correlation)) / 0.5, 1), 0)
        }
        
        self.strategy_fitness = sum(normalized[k] * v for k, v in weights.items())
        
        logger.debug(f"Calcolate metriche qualità: alpha={self.alpha:.4f}, "
                    f"beta={self.beta:.4f}, fitness={self.strategy_fitness:.4f}")
                    
    def to_dict(self) -> Dict[str, float]:
        """Converte le metriche in dizionario."""
        return {
            # Metriche di rendimento
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            
            # Metriche di rischio
            'max_drawdown': self.max_drawdown,
            'avg_drawdown': self.avg_drawdown,
            'drawdown_duration': self.drawdown_duration,
            'var_95': self.var_95,
            
            # Metriche operative
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'avg_trade': self.avg_trade,
            'num_trades': self.num_trades,
            
            # Metriche di qualità
            'strategy_fitness': self.strategy_fitness,
            'market_correlation': self.market_correlation,
            'alpha': self.alpha,
            'beta': self.beta
        }
