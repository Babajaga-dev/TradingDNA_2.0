"""Funzioni di ottimizzazione per il sistema DNA."""
from typing import Dict, Any
import pandas as pd
from rich.table import Table

from cli.utils import show_progress, console, print_error, print_success
from utils.logger_base import get_component_logger
from core.dna import DNA
from .dna import load_market_data

# Setup logger
logger = get_component_logger('DNAOptimization')

def handle_optimization(dna: DNA) -> None:
    """Gestisce l'ottimizzazione del DNA.
    
    Args:
        dna: Istanza del DNA
        
    Raises:
        ValueError: Se si verifica un errore nell'ottimizzazione
    """
    try:
        data = load_market_data()
        
        with show_progress("Ottimizzazione DNA") as progress:
            task = progress.add_task("Ottimizzazione...", total=100)
            
            for name, gene in dna.genes.items():
                gene.optimize(data)
                progress.update(task, advance=100/len(dna.genes))
                
        print_success("Ottimizzazione completata")
        
    except Exception as e:
        print_error(f"Errore ottimizzazione: {str(e)}")
        raise

def handle_validation(dna: DNA) -> None:
    """Gestisce la validazione del DNA.
    
    Args:
        dna: Istanza del DNA
        
    Raises:
        ValueError: Se si verifica un errore nella validazione
    """
    try:
        data = load_market_data()
        
        with show_progress("Validazione DNA") as progress:
            task = progress.add_task("Validazione...", total=100)
            
            metrics = {}
            for name, gene in dna.genes.items():
                metrics[name] = gene.metrics.calculate_fitness()
                progress.update(task, advance=100/len(dna.genes))
                
        table = Table(title="Metriche DNA")
        table.add_column("Gene", style="cyan")
        table.add_column("Fitness", style="green")
        
        for name, fitness in metrics.items():
            table.add_row(name, f"{fitness:.4f}")
            
        console.print("\n")
        console.print(table)
        
        print_success("Validazione completata")
        
    except Exception as e:
        print_error(f"Errore validazione: {str(e)}")
        raise
