"""Test suite for Capital Manager module."""
import pytest
from decimal import Decimal
from core.metabolism.capital_manager import CapitalManager

@pytest.fixture
def capital_manager():
    """Create a capital manager instance for testing."""
    return CapitalManager(
        initial_capital=Decimal('10000'),
        risk_limit=0.02
    )

def test_initial_capital():
    """Test initial capital setup."""
    manager = CapitalManager(Decimal('10000'), 0.02)
    assert manager.get_available_capital() == Decimal('10000')
    assert manager.get_total_exposure() == Decimal('0')

def test_capital_allocation():
    """Test capital allocation functionality."""
    manager = CapitalManager(Decimal('10000'), 0.02)
    
    # Test successful allocation
    assert manager.allocate_capital('strategy1', Decimal('5000'))
    assert manager.get_available_capital() == Decimal('5000')
    assert manager.get_total_exposure() == Decimal('5000')
    
    # Test allocation exceeding available capital
    assert not manager.allocate_capital('strategy2', Decimal('6000'))
    assert manager.get_available_capital() == Decimal('5000')

def test_capital_deallocation():
    """Test capital deallocation functionality."""
    manager = CapitalManager(Decimal('10000'), 0.02)
    
    # Allocate and deallocate
    manager.allocate_capital('strategy1', Decimal('3000'))
    deallocated = manager.deallocate_capital('strategy1')
    
    assert deallocated == Decimal('3000')
    assert manager.get_available_capital() == Decimal('10000')
    assert manager.get_total_exposure() == Decimal('0')
    
    # Test deallocation of non-existent strategy
    assert manager.deallocate_capital('non_existent') is None

def test_risk_budget():
    """Test risk budget management."""
    manager = CapitalManager(Decimal('10000'), 0.02)
    
    # Test setting valid risk budget
    assert manager.set_risk_budget('strategy1', 0.01)
    
    # Test setting risk budget exceeding limit
    assert not manager.set_risk_budget('strategy2', 0.03)

def test_strategy_allocation():
    """Test strategy allocation tracking."""
    manager = CapitalManager(Decimal('10000'), 0.02)
    
    manager.allocate_capital('strategy1', Decimal('2000'))
    manager.set_risk_budget('strategy1', 0.01)
    
    allocation = manager.get_strategy_allocation('strategy1')
    assert allocation is not None
    capital, risk = allocation
    
    assert capital == Decimal('2000')
    assert risk == 0.01

def test_allocation_summary():
    """Test allocation summary functionality."""
    manager = CapitalManager(Decimal('10000'), 0.02)
    
    manager.allocate_capital('strategy1', Decimal('3000'))
    manager.set_risk_budget('strategy1', 0.01)
    manager.allocate_capital('strategy2', Decimal('4000'))
    manager.set_risk_budget('strategy2', 0.015)
    
    summary = manager.get_allocation_summary()
    
    assert len(summary) == 2
    assert summary['strategy1']['capital'] == Decimal('3000')
    assert summary['strategy1']['risk_budget'] == 0.01
    assert summary['strategy2']['capital'] == Decimal('4000')
    assert summary['strategy2']['risk_budget'] == 0.015

def test_risk_limit_enforcement():
    """Test risk limit enforcement."""
    manager = CapitalManager(Decimal('10000'), 0.02)
    
    # Allocate to multiple strategies
    manager.allocate_capital('strategy1', Decimal('4000'))
    manager.set_risk_budget('strategy1', 0.015)
    
    # Try to exceed total risk limit
    assert not manager.set_risk_budget('strategy2', 0.01)

def test_capital_validation():
    """Test capital amount validation."""
    with pytest.raises(ValueError):
        CapitalManager(Decimal('-1000'), 0.02)
    
    with pytest.raises(ValueError):
        CapitalManager(Decimal('0'), 0.02)

def test_risk_limit_validation():
    """Test risk limit validation."""
    with pytest.raises(ValueError):
        CapitalManager(Decimal('1000'), -0.01)
    
    with pytest.raises(ValueError):
        CapitalManager(Decimal('1000'), 1.5)
