"""
Test per il sistema di logging
"""
import pytest
from pathlib import Path
import logging
from utils.logger import (
    setup_logging,
    get_logger,
    get_component_logger,
    get_progress_logger,
    ComponentLogger,
    ProgressLogger
)

@pytest.fixture
def setup_test_logging():
    """Setup logging per i test"""
    config_path = Path(__file__).parent.parent / "config" / "trace.yaml"
    setup_logging(str(config_path))
    yield
    # Cleanup handlers dopo ogni test
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

def test_basic_logging(setup_test_logging):
    """Test logging base"""
    logger = get_logger("test")
    logger.info("Test message")
    assert True  # Se arriviamo qui senza errori, il test passa

def test_component_logger(setup_test_logging):
    """Test ComponentLogger"""
    component = get_component_logger("dna")
    assert isinstance(component, ComponentLogger)
    component.info("Test DNA component")
    component.warning("Test warning")
    component.error("Test error")
    assert True

def test_progress_logger():
    """Test ProgressLogger"""
    with get_progress_logger() as progress:
        assert isinstance(progress, ProgressLogger)
        task_id = progress.add_task("Test task", total=100)
        for _ in range(10):
            progress.update(task_id, advance=10)
    assert True

def test_multiple_components(setup_test_logging):
    """Test multiple componenti contemporaneamente"""
    dna = get_component_logger("dna")
    immune = get_component_logger("immune")
    metabolism = get_component_logger("metabolism")
    
    dna.info("DNA test")
    immune.warning("Immune warning")
    metabolism.error("Metabolism error")
    assert True

def test_progress_with_components(setup_test_logging):
    """Test progress bar con log dei componenti"""
    dna = get_component_logger("dna")
    with get_progress_logger() as progress:
        task_id = progress.add_task("DNA Analysis", total=100)
        for i in range(10):
            progress.update(task_id, advance=10)
            dna.info(f"Processing step {i+1}")
    assert True

def test_log_levels(setup_test_logging):
    """Test diversi livelli di log"""
    logger = get_component_logger("test")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    assert True

def test_file_logging(setup_test_logging):
    """Test logging su file"""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    dna = get_component_logger("dna")
    dna.info("Test file logging")
    
    log_file = log_dir / "dna.log"
    assert log_file.exists()
    with open(log_file, 'r') as f:
        content = f.read()
        assert "Test file logging" in content
