"""Package DNA per il sistema di trading algoritmico.

Questo package contiene l'implementazione del sistema DNA che include:
- Classe base per i geni
- Implementazioni specifiche degli indicatori
- Pattern recognition
"""
from core.dna.base import Gene, DNA
from core.dna.rsi_gene import RSIGene
from core.dna.macd_gene import MACDGene
from core.dna.bollinger_gene import BollingerGene
from core.dna.volume_gene import VolumeGene

__all__ = [
    'Gene',
    'DNA',
    'RSIGene',
    'MACDGene', 
    'BollingerGene',
    'VolumeGene'
]
