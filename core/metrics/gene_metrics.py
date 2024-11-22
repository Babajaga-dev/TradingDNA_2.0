"""
Metriche per i geni del DNA system
"""
from dataclasses import dataclass
from typing import Dict
import numpy as np

from utils.logger_base import get_component_logger

# Setup logger
logger = get_component_logger('Metrics.Gene')

@dataclass
class GeneMetrics:
    """Metriche di performance per un gene."""
    win_rate: float = 0.0
    profit_factor: float = 0.0
    accuracy: float = 0.0
    adaptation_speed: float = 0.0
    signal_strength: float = 0.0
    noise_ratio: float = 0.0
    
    # Metriche per auto-tuning
    sensitivity: float = 0.0  # Sensibilità ai cambiamenti di mercato
    stability: float = 0.0    # Stabilità dei segnali nel tempo
    latency: float = 0.0      # Ritardo nella generazione segnali
    robustness: float = 0.0   # Robustezza a condizioni di mercato diverse
    
    def calculate_fitness(self) -> float:
        """Calcola il fitness score del gene."""
        weights = {
            'win_rate': 0.25,
            'profit_factor': 0.25,
            'accuracy': 0.15,
            'noise_ratio': 0.10,
            'stability': 0.10,
            'robustness': 0.15
        }
        
        score = (
            self.win_rate * weights['win_rate'] +
            self.profit_factor * weights['profit_factor'] +
            self.accuracy * weights['accuracy'] +
            (1 - self.noise_ratio) * weights['noise_ratio'] +
            self.stability * weights['stability'] +
            self.robustness * weights['robustness']
        )
        
        logger.debug(f"Calcolato fitness score: {score:.4f}")
        return score

    def to_dict(self) -> Dict[str, float]:
        """Converte le metriche in dizionario."""
        metrics = {
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'accuracy': self.accuracy,
            'adaptation_speed': self.adaptation_speed,
            'signal_strength': self.signal_strength,
            'noise_ratio': self.noise_ratio,
            'sensitivity': self.sensitivity,
            'stability': self.stability,
            'latency': self.latency,
            'robustness': self.robustness,
            'fitness': self.calculate_fitness()
        }
        logger.debug(f"Metriche gene convertite in dict: {metrics}")
        return metrics
        
    def update(self, results: Dict[str, float]) -> None:
        """Aggiorna le metriche con nuovi risultati."""
        for key, value in results.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"Aggiornata metrica {key}: {value}")
                
    def calculate_auto_tuning_metrics(self, signals: np.ndarray) -> None:
        """Calcola le metriche per l'auto-tuning."""
        if len(signals) < 2:
            return
            
        # Calcola stabilità (inverso della volatilità dei segnali)
        self.stability = 1.0 - np.std(signals)
        
        # Calcola sensibilità (media dei cambiamenti assoluti)
        changes = np.abs(np.diff(signals))
        self.sensitivity = np.mean(changes)
        
        # Calcola robustezza (percentuale di segnali non estremi)
        extreme_threshold = 0.8
        non_extreme = np.sum(np.abs(signals) < extreme_threshold)
        self.robustness = non_extreme / len(signals)
        
        logger.debug(f"Calcolate metriche auto-tuning: stability={self.stability:.4f}, "
                    f"sensitivity={self.sensitivity:.4f}, robustness={self.robustness:.4f}")
