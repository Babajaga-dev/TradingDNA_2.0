"""Gestione storage per il sistema di logging"""
import os
import gzip
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

class LogStorageManager:
    """Gestore dello storage dei log"""
    def __init__(self, config: dict):
        self.log_dir = Path(config['file']['path'])
        self.max_file_size = config['file']['max_size_kb'] * 1024  # Converti in bytes
        self.max_total_size = config['file']['max_total_size_mb'] * 1024 * 1024  # Converti in bytes
        self.retention_days = config['file']['retention']['days']
        self.compress_after_days = config['file']['retention']['compress_after_days']
        
        # Crea directory se non esiste
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def check_file_size(self, filepath: Path) -> bool:
        """Verifica se un file supera la dimensione massima"""
        if not filepath.exists():
            return True
        return filepath.stat().st_size <= self.max_file_size
        
    def get_total_size(self) -> int:
        """Calcola la dimensione totale della directory log"""
        total = 0
        if self.log_dir.exists():
            for file_path in self.log_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        total += file_path.stat().st_size
                    except OSError:
                        continue
        return total
        
    def check_total_size(self) -> bool:
        """Verifica se la directory supera la dimensione massima"""
        return self.get_total_size() <= self.max_total_size
        
    def clean_old_logs(self):
        """Pulisce i log vecchi basandosi sulla retention policy"""
        if not self.log_dir.exists():
            return
            
        now = datetime.now()
        files_to_remove = []
        
        # Prima fase: compressione e marcatura per eliminazione
        for filepath in self.log_dir.rglob('*.log'):
            try:
                file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                age_days = (now - file_time).days
                
                # Comprimi file vecchi non ancora compressi
                if age_days >= self.compress_after_days and not filepath.name.endswith('.gz'):
                    self._compress_file(filepath)
                    continue
                    
                # Marca per eliminazione file oltre retention
                if age_days >= self.retention_days:
                    files_to_remove.append(filepath)
                    
            except (OSError, ValueError) as e:
                logging.warning(f"Errore processando {filepath}: {e}")
                
        # Seconda fase: rimozione file marcati
        for filepath in files_to_remove:
            try:
                filepath.unlink()
            except OSError as e:
                logging.warning(f"Errore rimuovendo {filepath}: {e}")
                
        # Terza fase: rimozione file più vecchi se ancora sopra limite
        while not self.check_total_size():
            oldest_file = self._get_oldest_file()
            if oldest_file:
                try:
                    oldest_file.unlink()
                except OSError as e:
                    logging.warning(f"Errore rimuovendo {oldest_file}: {e}")
                    break
            else:
                break
                
    def _compress_file(self, filepath: Path):
        """Comprime un file di log"""
        try:
            compressed_path = filepath.with_suffix(filepath.suffix + '.gz')
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            filepath.unlink()  # Rimuove file originale
        except OSError as e:
            logging.warning(f"Errore comprimendo {filepath}: {e}")
            
    def _get_oldest_file(self) -> Optional[Path]:
        """Trova il file più vecchio nella directory log"""
        oldest_time = None
        oldest_file = None
        
        for filepath in self.log_dir.rglob('*'):
            if filepath.is_file():
                try:
                    mtime = filepath.stat().st_mtime
                    if oldest_time is None or mtime < oldest_time:
                        oldest_time = mtime
                        oldest_file = filepath
                except OSError:
                    continue
                    
        return oldest_file
