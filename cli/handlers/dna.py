"""
Handler per il Sistema DNA
"""
import time
import pandas as pd
from pathlib import Path
from rich.table import Table

from cli.utils import show_progress, console, create_progress, print_error, print_success
from core.dna import DNA
from utils.logger import get_component_logger

# Setup logger
logger = get_component_logger('CLI.DNA')

def print_dna_menu() -> Table:
    """Crea e restituisce la tabella del menu DNA"""
    table = Table(show_header=False, border_style="cyan", box=None)
    table.add_column("Option", style="cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("[1]", "🧬 Stato DNA         - Visualizza stato corrente")
    table.add_row("[2]", "➕ Aggiungi Gene    - Aggiungi nuovo gene")
    table.add_row("[3]", "➖ Rimuovi Gene     - Rimuovi gene esistente")
    table.add_row("[4]", "📊 Test Strategia   - Test su dati storici")
    table.add_row("[5]", "⚡ Ottimizza        - Ottimizza parametri")
    table.add_row("", "")
    table.add_row("[0]", "🔙 Indietro")
    
    return table

def handle_dna():
    """Gestisce il Sistema DNA"""
    logger.info("Avvio Sistema DNA")
    dna = DNA()  # Inizializza il sistema DNA
    
    while True:
        console.print("\n[bold cyan]🧬 Sistema DNA[/]")
        console.print(print_dna_menu())
        choice = console.input("\nSeleziona un'opzione [cyan][0-5][/]: ")
        
        if choice == '0':
            break
            
        elif choice == '1':  # Stato DNA
            if not dna.genes:
                console.print("[yellow]Nessun gene presente nel DNA[/]")
                logger.warning("Tentativo di visualizzare stato DNA senza geni")
            else:
                table = Table(title="Stato DNA", show_header=True)
                table.add_column("Gene", style="cyan")
                table.add_column("Fitness", style="green")
                table.add_column("Win Rate", style="yellow")
                table.add_column("Profit Factor", style="magenta")
                
                for name, gene in dna.genes.items():
                    metrics = gene.metrics.to_dict()
                    table.add_row(
                        name,
                        f"{metrics['fitness']:.2f}",
                        f"{metrics['win_rate']:.2f}",
                        f"{metrics['profit_factor']:.2f}"
                    )
                console.print(table)
                logger.info(f"Visualizzati {len(dna.genes)} geni")
                
        elif choice == '2':  # Aggiungi Gene
            logger.warning("Tentativo di aggiungere gene - funzionalità non implementata")
            print_error("Funzionalità in sviluppo")
            
        elif choice == '3':  # Rimuovi Gene
            if not dna.genes:
                logger.warning("Tentativo di rimuovere gene da DNA vuoto")
                print_error("Nessun gene presente nel DNA")
                continue
                
            table = Table(title="Seleziona Gene da Rimuovere", show_header=False)
            table.add_column("Option", style="cyan", width=4)
            table.add_column("Gene", style="white")
            
            genes = list(dna.genes.keys())
            for i, gene in enumerate(genes, 1):
                table.add_row(f"[{i}]", gene)
            
            console.print("\n")
            console.print(table)
            gene_choice = console.input(f"\nSeleziona gene [cyan][1-{len(genes)}][/]: ")
            
            if not gene_choice.isdigit() or int(gene_choice) < 1 or int(gene_choice) > len(genes):
                logger.warning(f"Selezione gene non valida: {gene_choice}")
                print_error("Scelta non valida")
                continue
                
            selected_gene = genes[int(gene_choice) - 1]
            dna.remove_gene(selected_gene)
            logger.info(f"Gene {selected_gene} rimosso")
            print_success(f"Gene {selected_gene} rimosso con successo")
            
        elif choice == '4':  # Test Strategia
            if not dna.genes:
                logger.warning("Tentativo di test strategia senza geni")
                print_error("Nessun gene presente nel DNA")
                continue
                
            try:
                # Carica dati di test
                data_path = Path("data/market/BTC_USDT_1h_testing.parquet")
                data = pd.read_parquet(data_path)
                logger.info(f"Caricati {len(data)} dati di test")
                
                with create_progress() as progress:
                    task = progress.add_task("[cyan]Test strategia...", total=len(data))
                    
                    signals = []
                    for i in range(len(data)):
                        window = data.iloc[:i+1]
                        signal = dna.get_strategy_signal(window)
                        signals.append(signal)
                        progress.update(task, advance=1)
                
                print_success("Test completato")
                console.print("Segnali generati:", len(signals))
                logger.info(f"Test completato: {len(signals)} segnali generati")
                
            except Exception as e:
                logger.error(f"Errore durante il test: {str(e)}")
                print_error(f"Errore durante il test: {str(e)}")
            
        elif choice == '5':  # Ottimizza
            if not dna.genes:
                logger.warning("Tentativo di ottimizzazione senza geni")
                print_error("Nessun gene presente nel DNA")
                continue
                
            try:
                # Carica dati di training
                data_path = Path("data/market/BTC_USDT_1h_training.parquet")
                data = pd.read_parquet(data_path)
                logger.info(f"Caricati {len(data)} dati di training")
                
                with create_progress() as progress:
                    task = progress.add_task("[cyan]Ottimizzazione...", total=len(dna.genes))
                    
                    for gene in dna.genes.values():
                        gene.optimize_params(data)
                        progress.update(task, advance=1)
                
                print_success("Ottimizzazione completata")
                logger.info("Ottimizzazione completata per tutti i geni")
                
            except Exception as e:
                logger.error(f"Errore durante l'ottimizzazione: {str(e)}")
                print_error(f"Errore durante l'ottimizzazione: {str(e)}")
            
        else:
            logger.warning(f"Opzione non valida: {choice}")
            print_error("Opzione non valida!")
            time.sleep(1)
            
        console.input("\nPremi INVIO per continuare...")
