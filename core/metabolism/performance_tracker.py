"""Performance Tracker Module.

This module handles performance metrics tracking and analysis
for the TradingDNA metabolism system.
"""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TradeMetrics:
    """Metrics for a single trade."""
    entry_price: Decimal
    exit_price: Decimal
    position_size: Decimal
    entry_time: datetime
    exit_time: datetime
    pnl: Decimal
    roi: float
    risk_reward_ratio: float

@dataclass
class PerformanceMetrics:
    """Overall performance metrics."""
    total_pnl: Decimal
    total_roi: float
    max_drawdown: float
    win_rate: float
    avg_win_loss_ratio: float
    sharpe_ratio: float
    sortino_ratio: float
    avg_holding_time: float

class PerformanceTracker:
    """Tracks and analyzes trading performance metrics."""

    def __init__(self, initial_capital: Decimal):
        """Initialize performance tracker.
        
        Args:
            initial_capital: Starting capital amount
        """
        self._initial_capital = initial_capital
        self._current_capital = initial_capital
        self._high_water_mark = initial_capital
        self._trades: Dict[str, TradeMetrics] = {}
        self._daily_balances: Dict[datetime, Decimal] = {}
        self._current_drawdown = Decimal('0')
        self._max_drawdown = Decimal('0')

    def record_trade(
        self,
        trade_id: str,
        entry_price: Decimal,
        exit_price: Decimal,
        position_size: Decimal,
        entry_time: datetime,
        exit_time: datetime,
        risk_amount: Decimal
    ) -> TradeMetrics:
        """Record a completed trade and calculate its metrics.
        
        Args:
            trade_id: Unique identifier for the trade
            entry_price: Entry price of the trade
            exit_price: Exit price of the trade
            position_size: Size of the position
            entry_time: Entry timestamp
            exit_time: Exit timestamp
            risk_amount: Amount risked on the trade
            
        Returns:
            TradeMetrics: Calculated metrics for the trade
        """
        # Calculate basic metrics
        pnl = (exit_price - entry_price) * position_size
        roi = float(pnl / (entry_price * position_size))
        
        # Calculate risk/reward ratio
        reward = abs(float(pnl))
        risk = float(risk_amount)
        risk_reward_ratio = reward / risk if risk != 0 else 0.0

        # Create trade metrics
        metrics = TradeMetrics(
            entry_price=entry_price,
            exit_price=exit_price,
            position_size=position_size,
            entry_time=entry_time,
            exit_time=exit_time,
            pnl=pnl,
            roi=roi,
            risk_reward_ratio=risk_reward_ratio
        )
        
        self._trades[trade_id] = metrics
        self._update_capital(pnl)
        
        return metrics

    def _update_capital(self, pnl: Decimal) -> None:
        """Update capital and drawdown metrics.
        
        Args:
            pnl: Profit/loss amount
        """
        self._current_capital += pnl
        
        # Update high water mark and drawdown
        if self._current_capital > self._high_water_mark:
            self._high_water_mark = self._current_capital
            self._current_drawdown = Decimal('0')
        else:
            self._current_drawdown = (
                (self._high_water_mark - self._current_capital) 
                / self._high_water_mark
            )
            
        if self._current_drawdown > self._max_drawdown:
            self._max_drawdown = self._current_drawdown

    def record_daily_balance(self, date: datetime) -> None:
        """Record end-of-day balance.
        
        Args:
            date: Date to record balance for
        """
        self._daily_balances[date] = self._current_capital

    def get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate overall performance metrics.
        
        Returns:
            PerformanceMetrics: Current performance metrics
        """
        if not self._trades:
            return PerformanceMetrics(
                total_pnl=Decimal('0'),
                total_roi=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                avg_win_loss_ratio=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                avg_holding_time=0.0
            )

        # Calculate basic metrics
        total_pnl = self._current_capital - self._initial_capital
        total_roi = float(total_pnl / self._initial_capital)
        
        # Calculate win rate
        winning_trades = [t for t in self._trades.values() if t.pnl > 0]
        win_rate = len(winning_trades) / len(self._trades)
        
        # Calculate average win/loss ratio
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else Decimal('0')
        losing_trades = [t for t in self._trades.values() if t.pnl < 0]
        avg_loss = abs(sum(t.pnl for t in losing_trades) / len(losing_trades)) if losing_trades else Decimal('1')
        avg_win_loss_ratio = float(avg_win / avg_loss) if avg_loss != 0 else 0.0
        
        # Calculate average holding time
        total_hours = sum(
            (t.exit_time - t.entry_time).total_seconds() / 3600 
            for t in self._trades.values()
        )
        avg_holding_time = total_hours / len(self._trades)
        
        # Calculate Sharpe and Sortino ratios
        # (simplified calculation - should use risk-free rate in practice)
        daily_returns = [
            (v - prev) / prev 
            for prev, v in zip(
                self._daily_balances.values(), 
                list(self._daily_balances.values())[1:]
            )
        ]
        
        if daily_returns:
            import statistics
            sharpe_ratio = statistics.mean(daily_returns) / statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0.0
            negative_returns = [r for r in daily_returns if r < 0]
            sortino_ratio = (
                statistics.mean(daily_returns) 
                / statistics.stdev(negative_returns) if negative_returns else 0.0
            )
        else:
            sharpe_ratio = 0.0
            sortino_ratio = 0.0

        return PerformanceMetrics(
            total_pnl=total_pnl,
            total_roi=total_roi,
            max_drawdown=float(self._max_drawdown),
            win_rate=win_rate,
            avg_win_loss_ratio=avg_win_loss_ratio,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            avg_holding_time=avg_holding_time
        )

    def get_trade_history(self) -> Dict[str, TradeMetrics]:
        """Get history of all recorded trades.
        
        Returns:
            Dict[str, TradeMetrics]: Trade metrics by ID
        """
        return self._trades.copy()

    def get_current_capital(self) -> Decimal:
        """Get current capital amount.
        
        Returns:
            Decimal: Current capital
        """
        return self._current_capital

    def get_current_drawdown(self) -> float:
        """Get current drawdown percentage.
        
        Returns:
            float: Current drawdown as percentage
        """
        return float(self._current_drawdown)

    def get_high_water_mark(self) -> Decimal:
        """Get highest recorded capital amount.
        
        Returns:
            Decimal: High water mark
        """
        return self._high_water_mark
