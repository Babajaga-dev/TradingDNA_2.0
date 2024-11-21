"""
Package per gli handler dei comandi CLI
"""
from cli.handlers.dna import handle_dna
from cli.handlers.log import handle_log
from cli.handlers.download import handle_download
from cli.handlers.config import handle_config

__all__ = ['handle_dna', 'handle_log', 'handle_download', 'handle_config']
