"""Test del sistema di logging"""
import pytest
import logging
import time
import os
import yaml
from pathlib import Path
from utils import (
    setup_logging,
    get_logger,
    get_component_logger,
    LogMetrics,
    LogStorageManager,
    PerformanceMonitor
)

@pytest.fixture
def test_config(tmp_path):
    """Fixture per configurazione di test"""
    config = {
        'global': {
            'log_level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S',
            'encoding': 'utf-8'
        },
        'file': {
            'enabled': True,
            'path': str(tmp_path),
            'max_size_kb': 400,
            'max_total_size_mb': 1,  # 1MB per test
            'backup_count': 3,
            'retention': {
                'days': 30,
                'compress_after_days': 7
            }
        },
        'console': {
            'enabled': True,
            'visual': True
        },
        'modules': {
            'test_module': {
                'level': 'DEBUG',
                'file': 'test.log',
                'console': True
            }
        }
    }
    
    # Crea config file temporaneo
    config_path = tmp_path / 'test_trace.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
        
    return config_path

def test_file_size_limit(test_config, tmp_path):
    """Verifica limite dimensione file"""
    with open(test_config, 'r') as f:
        config = yaml.safe_load(f)
    
    storage_manager = LogStorageManager(config)
    log_path = tmp_path / 'test.log'
    
    # Crea file oltre limite
    with open(log_path, 'w') as f:
        f.write('x' * 500 * 1024)  # 500KB
        
    assert not storage_manager.check_file_size(log_path)
    
    # Crea file entro limite
    with open(log_path, 'w') as f:
        f.write('x' * 300 * 1024)  # 300KB
        
    assert storage_manager.check_file_size(log_path)

def test_metrics_collection():
    """Verifica raccolta metriche"""
    metrics = LogMetrics()
    
    # Simula alcuni log
    metrics.increment_count('INFO')
    metrics.increment_count('ERROR')
    metrics.increment_count('WARNING')
    metrics.increment_count('ERROR')
    
    collected = metrics.get_metrics()
    assert collected['counts']['INFO'] == 1
    assert collected['counts']['ERROR'] == 2
    assert collected['counts']['WARNING'] == 1
    assert 'mttf' in collected

def test_performance_monitor():
    """Verifica monitor performance"""
    monitor = PerformanceMonitor()
    
    # Simula alcune scritture
    monitor.record_write(0.001)
    monitor.record_write(0.002)
    
    metrics = monitor.get_metrics()
    assert 'avg_write_time' in metrics
    assert 'cpu_usage' in metrics
    assert 'memory_usage' in metrics
    assert 'uptime' in metrics

def test_component_logger(caplog):
    """Verifica logger componenti"""
    logger = get_component_logger('DNA')
    
    with caplog.at_level(logging.INFO):
        logger.info('Test message')
        
    assert '🧬' in caplog.text
    assert 'DNA' in caplog.text
    assert 'Test message' in caplog.text

def test_log_rotation(test_config, tmp_path):
    """Verifica rotazione log"""
    metrics, storage = setup_logging(str(test_config))
    logger = get_logger('test_module')
    
    # Genera log fino a rotazione
    message = "Test message" * 50  # ~500 bytes per message
    for i in range(1000):  # Should generate ~500KB
        logger.info(f"{message} {i}")
        
    # Forza flush
    for handler in logger.handlers:
        handler.flush()
        
    time.sleep(0.1)  # Wait for file operations
    
    log_files = list(tmp_path.glob('*.log*'))
    assert len(log_files) > 1, f"Expected multiple log files, found: {log_files}"

def test_storage_cleanup(test_config, tmp_path):
    """Verifica pulizia storage"""
    with open(test_config, 'r') as f:
        config = yaml.safe_load(f)
    
    storage = LogStorageManager(config)
    
    # Crea alcuni file di test
    total_size = 0
    for i in range(5):
        file_path = tmp_path / f"test{i}.log"
        size = 300 * 1024  # 300KB per file
        with open(file_path, 'w') as f:
            f.write('x' * size)
        total_size += size
            
    # Verifica che il totale superi il limite (1MB)
    assert total_size > (config['file']['max_total_size_mb'] * 1024 * 1024)
    assert not storage.check_total_size()
    
    # Verifica pulizia
    storage.clean_old_logs()
    assert storage.check_total_size()

def test_metrics_reset():
    """Verifica reset metriche"""
    metrics = LogMetrics()
    
    metrics.increment_count('ERROR')
    metrics.increment_count('WARNING')
    
    metrics.reset_counts()
    assert all(count == 0 for count in metrics.log_counts.values())

def test_performance_thresholds():
    """Verifica soglie performance"""
    monitor = PerformanceMonitor()
    
    # Simula carico
    for _ in range(100):
        monitor.record_write(0.001)
        
    metrics = monitor.get_metrics()
    assert metrics['avg_write_time'] < 0.01  # Max 10ms
    assert metrics['memory_usage'] < 100  # Max 100MB

def test_error_tracking():
    """Verifica tracciamento errori"""
    metrics = LogMetrics()
    
    # Simula sequenza errori
    for _ in range(3):
        metrics.increment_count('ERROR')
        time.sleep(0.1)
        
    assert len(metrics.error_intervals) == 2
    assert metrics.get_mttf() > 0

def test_log_compression(test_config, tmp_path):
    """Verifica compressione log"""
    with open(test_config, 'r') as f:
        config = yaml.safe_load(f)
    
    storage = LogStorageManager(config)
    log_path = tmp_path / 'test.log'
    
    # Crea file da comprimere
    with open(log_path, 'w') as f:
        f.write('test log content')
        
    storage._compress_file(log_path)
    assert not log_path.exists()
    assert (log_path.parent / (log_path.name + '.gz')).exists()
