"""
Modulo di inizializzazione per TradingDNA 2.0
"""
import os
import sys
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any
import yaml
from colorama import Fore, Style

class InitializationError(Exception):
    """Eccezione per errori di inizializzazione"""
    pass

class Initializer:
    """Classe per gestire l'inizializzazione del sistema"""
    
    def __init__(self, force: bool = False):
        """
        Inizializza l'oggetto Initializer
        
        Args:
            force: Se True, forza la reinizializzazione anche se le directory esistono
        """
        self.force = force
        self.project_root = Path(__file__).parent.parent
        self.required_dirs = [
            'config',
            'core',
            'data',
            'logs',
            'tests',
            'utils'
        ]
        
    def print_progress(self, message: str, progress: int) -> None:
        """
        Stampa una barra di progresso
        
        Args:
            message: Messaggio da mostrare
            progress: Percentuale di completamento (0-100)
        """
        bar_width = 40
        filled = int(bar_width * progress / 100)
        bar = '━' * filled + '─' * (bar_width - filled)
        sys.stdout.write(f'\r{Fore.CYAN}{message} [{bar}] {progress}%{Style.RESET_ALL}')
        sys.stdout.flush()
        
    def create_directory_structure(self) -> None:
        """Crea la struttura delle directory del progetto"""
        total_dirs = len(self.required_dirs)
        
        for i, dir_name in enumerate(self.required_dirs, 1):
            dir_path = self.project_root / dir_name
            
            # Se force è True, ricrea la directory
            if self.force and dir_path.exists():
                shutil.rmtree(dir_path)
            
            dir_path.mkdir(exist_ok=not self.force)
            
            # Crea __init__.py se non esiste
            init_file = dir_path / "__init__.py"
            if not init_file.exists() or self.force:
                init_file.write_text(f'"""\n{dir_name.capitalize()} package per TradingDNA 2.0\n"""\n')
            
            progress = int((i / total_dirs) * 100)
            self.print_progress("Creazione struttura directory", progress)
            time.sleep(0.1)  # Simula lavoro
        print()  # Nuova linea dopo la progress bar
        
    def create_config_files(self) -> None:
        """Crea i file di configurazione di base"""
        config_templates = {
            'network.yaml': {
                'exchange': {
                    'name': 'binance',
                    'testnet': True,
                    'api': {
                        'key': '',
                        'secret': ''
                    }
                }
            },
            'trace.yaml': {
                'global': {
                    'log_level': 'INFO',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'portfolio.yaml': {
                'capital': {
                    'initial': 10000,
                    'reserve': 0.2
                }
            }
        }
        
        total_files = len(config_templates)
        config_dir = self.project_root / 'config'
        
        for i, (filename, template) in enumerate(config_templates.items(), 1):
            file_path = config_dir / filename
            
            # Se force è True o il file non esiste, crea/sovrascrivi
            if self.force or not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(template, f, default_flow_style=False)
            
            progress = int((i / total_files) * 100)
            self.print_progress("Creazione file configurazione", progress)
            time.sleep(0.1)  # Simula lavoro
        print()
        
    def initialize_git(self) -> None:
        """Inizializza il repository Git se non esiste"""
        git_dir = self.project_root / '.git'
        
        if not git_dir.exists() or self.force:
            if git_dir.exists():
                shutil.rmtree(git_dir)
            
            # Crea .gitignore se non esiste
            gitignore_path = self.project_root / '.gitignore'
            if not gitignore_path.exists() or self.force:
                gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
logs/
*.log

# Environment
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Project specific
config/*.yaml
data/
"""
                gitignore_path.write_text(gitignore_content.strip())
            
            self.print_progress("Inizializzazione Git", 50)
            time.sleep(0.1)
            self.print_progress("Inizializzazione Git", 100)
            print()
            
    def initialize(self) -> None:
        """
        Esegue l'inizializzazione completa del sistema
        
        Raises:
            InitializationError: Se ci sono errori durante l'inizializzazione
        """
        try:
            print(f"{Fore.CYAN}Inizializzazione TradingDNA 2.0...{Style.RESET_ALL}\n")
            
            # Crea struttura directory
            self.create_directory_structure()
            
            # Crea file configurazione
            self.create_config_files()
            
            # Inizializza Git
            self.initialize_git()
            
            print(f"\n{Fore.GREEN}✓ Sistema inizializzato con successo!{Style.RESET_ALL}")
            
        except Exception as e:
            raise InitializationError(f"Errore durante l'inizializzazione: {str(e)}")
