#!/usr/bin/env python3
"""
Script to download and prepare public biomedical datasets for DrugClaw

This script downloads commonly used public datasets that work well with DrugClaw.
All datasets are publicly available and free for research use.

Usage:
    python scripts/download_public_datasets.py --output-dir ./data
    python scripts/download_public_datasets.py --output-dir ./data --dataset chembl_drugs
    python scripts/download_public_datasets.py --list
"""

import argparse
import os
import sys
import zipfile
import tarfile
import logging
from pathlib import Path
from typing import List, Dict, Optional
import json

import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dataset definitions
DATASETS = {
    'chembl_drugs': {
        'description': 'ChEMBL drug-target interaction data (latest version)',
        'url': 'ftp://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_34_chemreps.txt.gz',
        'size_mb': 180,
        'license': 'CC-BY-SA 3.0',
        'requires_unpack': True
    },
    'drugbank_vocab': {
        'description': 'DrugBank vocabulary (open version)',
        'url': 'https://go.drugbank.com/releases/latest/downloads/drugbank-vocabulary.csv.zip',
        'size_mb': 5,
        'license': 'CC-BY 4.0 (requires free registration)',
        'requires_unpack': True
    },
    'sider_sideeffects': {
        'description': 'SIDER - drug side effects data',
        'url': 'http://sideeffects.embl.de/media/download/drugbankFrequency.zip',
        'size_mb': 2,
        'license': 'free for research',
        'requires_unpack': True
    },
    'admet_collection': {
        'description': 'ADMET benchmark collection from various sources',
        'url': 'https://github.com/yang-jinxin/ADMET-DB/raw/master/data/admet_data.zip',
        'size_mb': 10,
        'license': 'MIT',
        'requires_unpack': True
    },
    'zinc_15_sample': {
        'description': 'ZINC15 small sample for virtual screening testing',
        'url': 'https://files.docking.org/zinc15-20/untitled1/2k-compound-sample.smi.gz',
        'size_mb': 0.3,
        'license': 'free for research',
        'requires_unpack': False
    }
}

def download_file(url: str, output_path: Path) -> None:
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc=output_path.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            size = f.write(chunk)
            bar.update(size)

def unpack_file(file_path: Path, output_dir: Path) -> None:
    """Unpack compressed file"""
    logger.info(f"Unpacking {file_path} to {output_dir}")
    
    if file_path.suffix == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
    elif file_path.suffix == '.gz':
        import gzip
        output_file = output_dir / file_path.stem
        with gzip.open(file_path, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
    elif tarfile.is_tarfile(file_path):
        with tarfile.open(file_path, 'r') as tar_ref:
            tar_ref.extractall(output_dir)
    else:
        logger.warning(f"Unknown compression format for {file_path}")

def list_datasets():
    """List all available datasets"""
    print("=== Available Public Datasets for DrugClaw ===\n")
    for name, info in DATASETS.items():
        print(f"**{name}**")
        print(f"  Description: {info['description']}")
        print(f"  Size: {info['size_mb']:.1f} MB")
        print(f"  License: {info['license']}")
        print()

def download_dataset(dataset_name: str, output_dir: Path) -> None:
    """Download a specific dataset"""
    if dataset_name not in DATASETS:
        logger.error(f"Dataset {dataset_name} not found")
        logger.info("Available datasets: " + ", ".join(DATASETS.keys()))
        sys.exit(1)
    
    info = DATASETS[dataset_name]
    dataset_dir = output_dir / dataset_name
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    url = info['url']
    filename = os.path.basename(url)
    output_path = dataset_dir / filename
    
    if output_path.exists():
        logger.info(f"File already exists: {output_path}")
        if info['requires_unpack']:
            unpack_file(output_path, dataset_dir)
        return
    
    logger.info(f"Downloading {dataset_name} from {url}")
    download_file(url, output_path)
    
    if info['requires_unpack']:
        unpack_file(output_path, dataset_dir)
    
    # Save metadata
    with open(dataset_dir / 'metadata.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    logger.info(f"✅ {dataset_name} downloaded and prepared to {dataset_dir}")

def download_all(output_dir: Path):
    """Download all available datasets"""
    total_size = sum(info['size_mb'] for info in DATASETS.values())
    logger.info(f"Downloading all datasets (total ~{total_size:.1f} MB)...")
    
    for dataset_name in DATASETS:
        download_dataset(dataset_name, output_dir)
    
    logger.info("✅ All datasets downloaded!")

def main():
    parser = argparse.ArgumentParser(
        description='Download public biomedical datasets for DrugClaw'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available datasets'
    )
    parser.add_argument(
        '--dataset', '-d',
        type=str,
        help='Download specific dataset'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='./data',
        help='Output directory for downloaded data'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Download all available datasets'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_datasets()
        return
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.all:
        download_all(output_dir)
    elif args.dataset:
        download_dataset(args.dataset, output_dir)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
