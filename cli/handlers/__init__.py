"""
CLI Handlers
"""
from cli.handlers.log import handle_log
from cli.handlers.download import handle_download
from cli.handlers.config import handle_config
from cli.handlers.dna import handle_dna

__all__ = ['handle_log', 'handle_download', 'handle_config', 'handle_dna']
