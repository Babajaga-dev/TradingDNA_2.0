"""Capital Manager Module.

This module handles capital allocation, risk budgeting and performance tracking
for the TradingDNA metabolism system.
"""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging
from core.immune_system import ImmuneSystem
from utils.logger_base import get_logger

class CapitalManager:
    """Manages capital allocation and risk budgeting."""

    def __init__(
        self,
        initial_capital: Decimal,
        risk_limit: float = 0.02,
        immune_system: Optional[ImmuneSystem] = None
    ):
        """Initialize capital manager.
        
        Args:
            initial_capital: Starting capital amount
            risk_limit: Maximum risk per trade as percentage (default 2%)
            immune_system: Optional immune system instance for risk management
            
        Raises:
            ValueError: If initial_capital <= 0 or risk_limit invalid
        """
        if initial_capital <= Decimal('0'):
            raise ValueError("Initial capital must be positive")
        if not 0 < risk_limit < 1:
            raise ValueError("Risk limit must be between 0 and 1")

        self._capital = initial_capital
        self._risk_limit = risk_limit
        self._immune_system = immune_system
        self._allocated_capital: Dict[str, Decimal] = {}
        self._risk_budget: Dict[str, float] = {}
        self._logger = get_logger(__name__)
        
        self._logger.info(
            "Initialized CapitalManager with capital=%s, risk_limit=%s",
            initial_capital, risk_limit
        )

    def allocate_capital(self, strategy_id: str, amount: Decimal) -> bool:
        """Allocate capital to a specific strategy.
        
        Args:
            strategy_id: Unique identifier for the strategy
            amount: Amount of capital to allocate
            
        Returns:
            bool: True if allocation successful, False if insufficient funds
        """
        if amount <= Decimal('0'):
            self._logger.error(
                "Invalid allocation amount: %s for strategy %s",
                amount, strategy_id
            )
            return False

        if amount > self._capital:
            self._logger.warning(
                "Insufficient funds for allocation: requested=%s, available=%s",
                amount, self._capital
            )
            return False
            
        # Check with immune system if available
        if self._immune_system and not self._immune_system.validate_allocation(
            strategy_id, float(amount)
        ):
            self._logger.warning(
                "Allocation rejected by immune system for strategy %s",
                strategy_id
            )
            return False

        self._allocated_capital[strategy_id] = amount
        self._capital -= amount
        
        self._logger.info(
            "Allocated %s to strategy %s. Remaining capital: %s",
            amount, strategy_id, self._capital
        )
        return True

    def deallocate_capital(self, strategy_id: str) -> Optional[Decimal]:
        """Deallocate capital from a strategy.
        
        Args:
            strategy_id: Unique identifier for the strategy
            
        Returns:
            Optional[Decimal]: Amount deallocated or None if strategy not found
        """
        if strategy_id not in self._allocated_capital:
            self._logger.warning(
                "Attempted to deallocate non-existent strategy: %s",
                strategy_id
            )
            return None
            
        amount = self._allocated_capital[strategy_id]
        del self._allocated_capital[strategy_id]
        self._capital += amount
        
        if strategy_id in self._risk_budget:
            del self._risk_budget[strategy_id]
        
        self._logger.info(
            "Deallocated %s from strategy %s. Available capital: %s",
            amount, strategy_id, self._capital
        )
        return amount

    def set_risk_budget(self, strategy_id: str, risk_percentage: float) -> bool:
        """Set risk budget for a strategy.
        
        Args:
            strategy_id: Unique identifier for the strategy
            risk_percentage: Maximum risk allocation as percentage
            
        Returns:
            bool: True if risk budget set successfully
        """
        if not 0 < risk_percentage < 1:
            self._logger.error(
                "Invalid risk percentage: %s for strategy %s",
                risk_percentage, strategy_id
            )
            return False

        # Check total risk budget including immune system limits
        total_risk = sum(self._risk_budget.values()) + risk_percentage
        if total_risk > self._risk_limit:
            self._logger.warning(
                "Risk budget exceeded: total=%s, limit=%s",
                total_risk, self._risk_limit
            )
            return False
            
        # Validate with immune system
        if self._immune_system and not self._immune_system.validate_risk(
            strategy_id, risk_percentage
        ):
            self._logger.warning(
                "Risk budget rejected by immune system for strategy %s",
                strategy_id
            )
            return False
            
        self._risk_budget[strategy_id] = risk_percentage
        
        self._logger.info(
            "Set risk budget %s for strategy %s. Total risk: %s",
            risk_percentage, strategy_id, total_risk
        )
        return True

    def get_available_capital(self) -> Decimal:
        """Get available unallocated capital.
        
        Returns:
            Decimal: Amount of unallocated capital
        """
        return self._capital

    def get_total_exposure(self) -> Decimal:
        """Get total capital exposure across all strategies.
        
        Returns:
            Decimal: Total allocated capital
        """
        return sum(self._allocated_capital.values())

    def get_strategy_allocation(self, strategy_id: str) -> Optional[Tuple[Decimal, float]]:
        """Get capital and risk allocation for a strategy.
        
        Args:
            strategy_id: Unique identifier for the strategy
            
        Returns:
            Optional[Tuple[Decimal, float]]: (allocated capital, risk budget) or None
        """
        if strategy_id not in self._allocated_capital:
            return None
            
        return (
            self._allocated_capital[strategy_id],
            self._risk_budget.get(strategy_id, 0.0)
        )

    def get_allocation_summary(self) -> Dict[str, Dict]:
        """Get summary of all capital and risk allocations.
        
        Returns:
            Dict[str, Dict]: Summary of allocations per strategy
        """
        return {
            strategy_id: {
                'capital': amount,
                'risk_budget': self._risk_budget.get(strategy_id, 0.0)
            }
            for strategy_id, amount in self._allocated_capital.items()
        }

    def validate_strategy_health(self, strategy_id: str) -> bool:
        """Validate strategy health with immune system.
        
        Args:
            strategy_id: Unique identifier for the strategy
            
        Returns:
            bool: True if strategy is healthy
        """
        if not self._immune_system:
            return True
            
        is_healthy = self._immune_system.check_strategy_health(strategy_id)
        
        if not is_healthy:
            self._logger.warning(
                "Strategy %s failed health check",
                strategy_id
            )
            
        return is_healthy
