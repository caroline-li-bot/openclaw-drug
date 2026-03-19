#!/usr/bin/env python3
"""
Batch parallel docking for large compound libraries
Uses multiprocessing for parallel docking on multiple CPUs
"""

import os
import multiprocessing
from typing import List, Tuple, Dict, Optional
import logging
from pathlib import Path

from drugclaw.virtual_screening.prep import prepare_receptor, prepare_ligand_from_smiles
from drugclaw.virtual_screening.docking import run_vina_docking
from drugclaw.virtual_screening.analysis import analyze_results

logger = logging.getLogger(__name__)

def worker(args):
    """Worker process for parallel docking"""
    idx, smiles, name, receptor_pdbqt, center, box_size, output_dir = args
    
    try:
        ligand_pdbqt = prepare_ligand_from_smiles(smiles, name, output_dir)
        if ligand_pdbqt is None:
            logger.warning(f"Failed to prepare ligand {name}")
            return (idx, smiles, None)
        
        affinity = run_vina_docking(
            receptor_pdbqt, ligand_pdbqt,
            center, box_size,
            cpu=1,  # One CPU per ligand, parallel across ligands
            output_dir=output_dir
        )
        
        return (idx, smiles, affinity)
    except Exception as e:
        logger.error(f"Exception docking {name}: {str(e)}")
        return (idx, smiles, None)

def run_parallel_screening(
    receptor_pdb: str,
    center: Tuple[float, float, float],
    box_size: Tuple[float, float, float],
    smiles_csv: str,
    output_dir: str = "./docking_output",
    num_cpus: Optional[int] = None,
    chunk_size: int = 1000
) -> List[Dict]:
    """
    Run parallel virtual screening for a large compound library
    
    Args:
        receptor_pdb: Path to receptor PDB
        center: Binding pocket center (x, y, z)
        box_size: Box size (sx, sy, sz)
        smiles_csv: CSV with 'smiles' column (optional 'name' column)
        output_dir: Directory for output
        num_cpus: Number of parallel processes (defaults to all available)
        chunk_size: Save results every N compounds
    
    Returns:
        List of results: [{'index': idx, 'smiles': smiles, 'affinity_kcal_mol': affinity}]
    """
    import pandas as pd
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare receptor
    logger.info(f"Preparing receptor: {receptor_pdb}")
    receptor_pdbqt = prepare_receptor(receptor_pdb)
    
    # Read compounds
    df = pd.read_csv(smiles_csv)
    if 'smiles' not in df.columns:
        raise ValueError("CSV must have 'smiles' column")
    
    if 'name' not in df.columns:
        df['name'] = [f"ligand_{i}" for i in range(len(df))]
    
    logger.info(f"Starting parallel docking for {len(df)} compounds")
    
    # Prepare tasks
    tasks = []
    for idx, row in df.iterrows():
        tasks.append((
            idx,
            row['smiles'],
            row['name'],
            receptor_pdbqt,
            center,
            box_size,
            output_dir
        ))
    
    # Determine number of processes
    if num_cpus is None:
        num_cpus = max(1, multiprocessing.cpu_count() - 1)
    
    logger.info(f"Using {num_cpus} parallel processes")
    
    # Run parallel
    results = []
    failed = 0
    
    with multiprocessing.Pool(num_cpus) as pool:
        for result in pool.imap_unordered(worker, tasks):
            idx, smiles, affinity = result
            if affinity is not None:
                results.append({
                    'index': idx,
                    'smiles': smiles,
                    'affinity_kcal_mol': affinity
                })
            else:
                failed += 1
    
    logger.info(f"Docking complete: {len(results)} succeeded, {failed} failed")
    
    return results

def save_results(results: List[Dict], output_csv: str) -> None:
    """Save results to CSV"""
    import pandas as pd
    df = pd.DataFrame(results)
    df = df.sort_values('affinity_kcal_mol', ascending=True)
    df = df.reset_index(drop=True)
    df['rank'] = df.index + 1
    df.to_csv(output_csv, index=False)
    logger.info(f"Results saved to {output_csv}")

def main():
    """Command line interface for parallel screening"""
    import argparse
    parser = argparse.ArgumentParser(
        description="Parallel virtual screening with AutoDock Vina"
    )
    parser.add_argument(
        '--receptor', '-r',
        required=True,
        help='Input receptor PDB file'
    )
    parser.add_argument(
        '--center-x', '-cx',
        type=float,
        required=True,
        help='Binding pocket center X'
    )
    parser.add_argument(
        '--center-y', '-cy',
        type=float,
        required=True,
        help='Binding pocket center Y'
    )
    parser.add_argument(
        '--center-z', '-cz',
        type=float,
        required=True,
        help='Binding pocket center Z'
    )
    parser.add_argument(
        '--size-x', '-sx',
        type=float,
        default=20.0,
        help='Box size X'
    )
    parser.add_argument(
        '--size-y', '-sy',
        type=float,
        default=20.0,
        help='Box size Y'
    )
    parser.add_argument(
        '--size-z', '-sz',
        type=float,
        default=20.0,
        help='Box size Z'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input CSV file with smiles column'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output CSV file for results'
    )
    parser.add_argument(
        '--output-dir', '-d',
        default='./docking_output',
        help='Output directory for intermediate PDBQT files'
    )
    parser.add_argument(
        '--cpus', '-c',
        type=int,
        default=None,
        help='Number of parallel CPUs (default: all available)'
    )
    
    args = parser.parse_args()
    
    center = (args.center_x, args.center_y, args.center_z)
    box_size = (args.size_x, args.size_y, args.size_z)
    
    results = run_parallel_screening(
        args.receptor,
        center,
        box_size,
        args.input,
        args.output_dir,
        args.cpus
    )
    
    save_results(results, args.output)
    
    # Print summary
    print(f"\n=== Parallel Virtual Screening Complete ===")
    print(f"Total compounds: {len(results) + (len(results) - len([r for r in results if r['affinity_kcal_mol'] is not None]))}")
    print(f"Succeeded: {len(results)}")
    print(f"Failed: {len(results) - len([r for r in results if r['affinity_kcal_mol'] is not None])}")
    if results:
        print(f"\nTop 5 compounds by binding affinity:")
        import pandas as pd
        df = pd.DataFrame(results)
        df = df.sort_values('affinity_kcal_mol', ascending=True)
        print(df.head().to_string(index=False))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
