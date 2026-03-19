#!/usr/bin/env python3
"""
Deterministic retrieval/run for AutoDock Vina virtual screening
Usage: python retrieve.py receptor_pdb center_x center_y center_z box_size_x box_size_y box_size_z smiles_csv output_csv
"""

import sys
import argparse
import pandas as pd
from drugclaw.virtual_screening.prep import prepare_receptor
from drugclaw.virtual_screening.batch_parallel import run_parallel_screening, save_results

def main():
    parser = argparse.ArgumentParser(
        description="AutoDock Vina Virtual Screening with parallel processing"
    )
    parser.add_argument(
        'receptor_pdb',
        help='Input receptor PDB file'
    )
    parser.add_argument(
        'center_x', type=float,
        help='Binding pocket center X coordinate'
    )
    parser.add_argument(
        'center_y', type=float,
        help='Binding pocket center Y coordinate'
    )
    parser.add_argument(
        'center_z', type=float,
        help='Binding pocket center Z coordinate'
    )
    parser.add_argument(
        'size_x', type=float, default=20.0,
        help='Box size X in Angstrom (default: 20.0)'
    )
    parser.add_argument(
        'size_y', type=float, default=20.0,
        help='Box size Y in Angstrom (default: 20.0)'
    )
    parser.add_argument(
        'size_z', type=float, default=20.0,
        help='Box size Z in Angstrom (default: 20.0)'
    )
    parser.add_argument(
        'smiles_csv',
        help='Input CSV file with "smiles" column'
    )
    parser.add_argument(
        'output_csv',
        help='Output CSV file for ranked results'
    )
    parser.add_argument(
        '--output-dir', '-d', default='./docking_output',
        help='Output directory for intermediate PDBQT files'
    )
    parser.add_argument(
        '--cpus', '-c', type=int, default=None,
        help='Number of parallel CPUs (default: all available)'
    )
    
    args = parser.parse_args()
    
    center = (args.center_x, args.center_y, args.center_z)
    box_size = (args.size_x, args.size_y, args.size_z)
    
    print(f"=== Starting AutoDock Vina Virtual Screening (Parallel) ===")
    print(f"Receptor: {args.receptor_pdb}")
    print(f"Binding pocket center: {center}")
    print(f"Box size: {box_size}")
    print(f"Input compounds: {args.smiles_csv}")
    print(f"Output results: {args.output_csv}")
    print(f"Output directory: {args.output_dir}")
    if args.cpus:
        print(f"Using {args.cpus} parallel CPUs")
    print()
    
    # Step 1: Prepare receptor
    print("1/3 Preparing receptor...")
    receptor_pdbqt = prepare_receptor(args.receptor_pdb)
    print(f"   Receptor prepared: {receptor_pdbqt}")
    
    # Step 2: Run parallel docking
    print(f"\n2/3 Running parallel docking...")
    results = run_parallel_screening(
        args.receptor_pdb,
        center,
        box_size,
        args.smiles_csv,
        args.output_dir,
        args.cpus
    )
    
    # Step 3: Save and analyze
    print(f"\n3/3 Saving results...")
    save_results(results, args.output_csv)
    
    df_results = pd.read_csv(args.output_csv)
    
    print(f"\n✅ Done!")
    print(f"   Total compounds: {len(df_results)}")
    print(f"   Successful docking: {len(df_results.dropna())}")
    print(f"\nTop 5 compounds by binding affinity (lower = better):")
    print(df_results.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
