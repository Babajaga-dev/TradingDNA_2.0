#!/usr/bin/env python3
"""
TradingDNA 2.0 - Command Line Interface
"""
import sys
import argparse
import logging

from utils.logger_base import setup_logging
from cli.menu import MainMenu
from cli.commands import (
    handle_init, handle_nervous, 
    handle_endocrine, handle_reproductive
)
from cli.handlers import handle_config, handle_download, handle_log

def setup_argparse() -> argparse.ArgumentParser:
    """Configura il parser degli argomenti CLI"""
    parser = argparse.ArgumentParser(
        description="TradingDNA 2.0 - Sistema di Trading Algoritmico Biologico",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Comandi principali
    subparsers = parser.add_subparsers(dest="command", help="Comandi disponibili")
    
    # Comando: menu
    subparsers.add_parser("menu", help="Mostra menu interattivo")
    
    # Comando: init
    init_parser = subparsers.add_parser("init", help="Inizializza il sistema")
    init_parser.add_argument("--force", action="store_true", help="Forza reinizializzazione")
    
    # Comando: config
    config_parser = subparsers.add_parser("config", help="Gestione configurazione")
    config_parser.add_argument("action", choices=["validate", "show"], help="Azione configurazione")
    config_parser.add_argument("--file", help="File di configurazione specifico")
    
    # Comando: download
    download_parser = subparsers.add_parser("download", help="Download dati mercato")
    download_parser.add_argument("--dataset", choices=["training", "testing", "paper_trading", "all"],
                               default="all", help="Dataset da scaricare")
    download_parser.add_argument("--pair", help="Coppia di trading (es. BTC/USDT)")
    download_parser.add_argument("--timeframe", help="Timeframe specifico")
    download_parser.add_argument("--progress", action="store_true", help="Mostra barra progresso")
    
    # Comando: log
    log_parser = subparsers.add_parser("log", help="Gestione logging")
    log_parser.add_argument("action", choices=["show", "clear", "test"], help="Azione logging")
    log_parser.add_argument("--module", help="Modulo specifico")
    
    return parser

def main():
    """Funzione principale CLI"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging()
    
    # Mapping comandi
    commands = {
        "menu": lambda _: MainMenu().run(),  # Usa run() invece di display_menu()
        "init": handle_init,
        "config": handle_config,
        "download": handle_download,
        "log": handle_log
    }
    
    try:
        # Esegui comando
        commands[args.command](args)
    except KeyboardInterrupt:
        logging.warning("Operazione interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Errore: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
