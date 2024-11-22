"""Position Sizer Module.

This module handles dynamic position sizing and exposure management
for the TradingDNA metabolism system.
"""
from typing import Dict, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass
import logging
from core.dna.dna import DNA
from utils.logger_base import get_logger

@dataclass
class PositionConfig:
    """Configuration for position sizing."""
    max_position_size: Decimal
    risk_per_trade: float
    stop_loss_pct: float
    max_exposure_pct: float

    def __post_init__(self):
        """Validate configuration parameters."""
        if self.max_position_size <= Decimal('0'):
            raise ValueError("Maximum position size must be positive")
        if not 0 < self.risk_per_trade < 1:
            raise ValueError("Risk per trade must be between 0 and 1")
        if not 0 < self.stop_loss_pct < 1:
            raise ValueError("Stop loss percentage must be between 0 and 1")
        if not 0 < self.max_exposure_pct <= 1:
            raise ValueError("Maximum exposure must be between 0 and 1")

class PositionSizer:
    """Handles position sizing and exposure management."""

    def __init__(self, position_config: PositionConfig, dna_system: Optional[DNA] = None):
        """Initialize position sizer.
        
        Args:
            position_config: Configuration for position sizing
            dna_system: Optional DNA system for signal integration
        """
        self._config = position_config
        self._dna_system = dna_system
        self._active_positions: Dict[str, Decimal] = {}
        self._total_exposure: Decimal = Decimal('0')
        self._logger = get_logger(__name__)
        
        self._logger.info(
            "Initialized PositionSizer with config: %s",
            position_config
        )

    def calculate_position_size(
        self,
        capital: Decimal,
        entry_price: Decimal,
        stop_loss: Optional[Decimal] = None,
        signal_strength: float = 1.0
    ) -> Tuple[Decimal, Dict]:
        """Calculate position size based on available capital and risk parameters.
        
        Args:
            capital: Available capital for the trade
            entry_price: Entry price for the position
            stop_loss: Optional stop loss price
            signal_strength: Signal strength from DNA system (0.0-1.0)
            
        Returns:
            Tuple[Decimal, Dict]: Position size and sizing metrics
        """
        if capital <= Decimal('0'):
            raise ValueError("Capital must be positive")
        if entry_price <= Decimal('0'):
            raise ValueError("Entry price must be positive")
        if stop_loss and stop_loss <= Decimal('0'):
            raise ValueError("Stop loss price must be positive")
        if not 0 <= signal_strength <= 1:
            raise ValueError("Signal strength must be between 0 and 1")

        # Calculate risk amount
        risk_amount = capital * Decimal(str(self._config.risk_per_trade))
        self._logger.debug("Risk amount calculated: %s", risk_amount)
        
        # Calculate base position size from risk
        if stop_loss:
            price_risk = abs(entry_price - stop_loss) / entry_price
            base_size = risk_amount / (entry_price * Decimal(str(price_risk)))
            self._logger.debug(
                "Position size from stop loss: price_risk=%s, base_size=%s",
                price_risk, base_size
            )
        else:
            # Use default stop loss percentage if no price provided
            base_size = risk_amount / (entry_price * Decimal(str(self._config.stop_loss_pct)))
            self._logger.debug(
                "Position size from default stop: stop_pct=%s, base_size=%s",
                self._config.stop_loss_pct, base_size
            )

        # Adjust for signal strength
        adjusted_size = base_size * Decimal(str(signal_strength))
        self._logger.debug(
            "Size adjusted for signal strength: strength=%s, size=%s",
            signal_strength, adjusted_size
        )
        
        # Apply position limits
        final_size = min(
            adjusted_size,
            self._config.max_position_size,
            capital / entry_price
        )
        
        self._logger.info(
            "Final position size calculated: %s (capital=%s, entry=%s)",
            final_size, capital, entry_price
        )

        metrics = {
            'base_size': base_size,
            'signal_adjustment': signal_strength,
            'risk_amount': risk_amount,
            'final_size': final_size
        }

        return final_size, metrics

    def can_open_position(
        self,
        position_id: str,
        size: Decimal,
        capital: Decimal
    ) -> bool:
        """Check if new position can be opened within exposure limits.
        
        Args:
            position_id: Unique identifier for the position
            size: Proposed position size
            capital: Total available capital
            
        Returns:
            bool: True if position can be opened
        """
        if position_id in self._active_positions:
            self._logger.warning(
                "Position %s already exists",
                position_id
            )
            return False

        new_exposure = self._total_exposure + size
        max_exposure = capital * Decimal(str(self._config.max_exposure_pct))
        
        can_open = new_exposure <= max_exposure
        if not can_open:
            self._logger.warning(
                "Opening position would exceed max exposure: current=%s, new=%s, max=%s",
                self._total_exposure, new_exposure, max_exposure
            )
            
        return can_open

    def open_position(self, position_id: str, size: Decimal) -> bool:
        """Record opening of a new position.
        
        Args:
            position_id: Unique identifier for the position
            size: Position size
            
        Returns:
            bool: True if position recorded successfully
        """
        if position_id in self._active_positions:
            self._logger.warning(
                "Cannot open duplicate position: %s",
                position_id
            )
            return False
            
        self._active_positions[position_id] = size
        self._total_exposure += size
        
        self._logger.info(
            "Opened position %s with size %s. Total exposure: %s",
            position_id, size, self._total_exposure
        )
        return True

    def close_position(self, position_id: str) -> Optional[Decimal]:
        """Record closing of an existing position.
        
        Args:
            position_id: Unique identifier for the position
            
        Returns:
            Optional[Decimal]: Closed position size or None if not found
        """
        if position_id not in self._active_positions:
            self._logger.warning(
                "Cannot close non-existent position: %s",
                position_id
            )
            return None
            
        size = self._active_positions[position_id]
        del self._active_positions[position_id]
        self._total_exposure -= size
        
        self._logger.info(
            "Closed position %s with size %s. Total exposure: %s",
            position_id, size, self._total_exposure
        )
        return size

    def get_position_exposure(self) -> Dict[str, Decimal]:
        """Get current exposure for all active positions.
        
        Returns:
            Dict[str, Decimal]: Position sizes by ID
        """
        return self._active_positions.copy()

    def get_total_exposure(self) -> Decimal:
        """Get total exposure across all positions.
        
        Returns:
            Decimal: Total exposure
        """
        return self._total_exposure

    def update_position_size(
        self,
        position_id: str,
        new_size: Decimal
    ) -> Optional[Tuple[Decimal, Decimal]]:
        """Update size of an existing position.
        
        Args:
            position_id: Unique identifier for the position
            new_size: New position size
            
        Returns:
            Optional[Tuple[Decimal, Decimal]]: (old size, new size) or None
        """
        if position_id not in self._active_positions:
            self._logger.warning(
                "Cannot update non-existent position: %s",
                position_id
            )
            return None
            
        old_size = self._active_positions[position_id]
        self._active_positions[position_id] = new_size
        self._total_exposure = self._total_exposure - old_size + new_size
        
        self._logger.info(
            "Updated position %s size: %s -> %s. Total exposure: %s",
            position_id, old_size, new_size, self._total_exposure
        )
        return (old_size, new_size)

    def get_dna_signal_strength(self, symbol: str) -> float:
        """Get signal strength from DNA system.
        
        Args:
            symbol: Trading symbol to get signal for
            
        Returns:
            float: Signal strength between 0 and 1
        """
        if not self._dna_system:
            return 1.0
            
        signal = self._dna_system.get_signal_strength(symbol)
        
        self._logger.debug(
            "DNA signal strength for %s: %s",
            symbol, signal
        )
        
        return signal
