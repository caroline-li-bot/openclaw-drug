# DrugClaw Makefile
# Convenience commands for dataset download and processing

# Default directory for data
DATA_DIR ?= ./data
RAG_DB ?= ./data/chroma_db

# List available datasets
list-datasets:
	@python scripts/download_public_datasets.py --list

# Download all datasets
download-all:
	@python scripts/download_public_datasets.py --all --output-dir $(DATA_DIR)

# Download specific dataset
download-%:
	@python scripts/download_public_datasets.py --dataset $* --output-dir $(DATA_DIR)

# Import all PDFs from a directory to RAG
import-pdfs:
ifndef INPUT_DIR
	$(error INPUT_DIR is required: make import-pdfs INPUT_DIR=./pdfs)
endif
	@python scripts/import_pdfs_to_rag.py --input-dir $(INPUT_DIR) --db-path $(RAG_DB)

# Build knowledge graph from CSV
build-kg:
ifndef INPUT_CSV
	$(error INPUT_CSV is required: make build-kg INPUT_CSV=./dti.csv OUTPUT_KG=./kg.json)
endif
ifndef OUTPUT_KG
	$(error OUTPUT_KG is required: make build-kg INPUT_CSV=./dti.csv OUTPUT_KG=./kg.json)
endif
	@python scripts/build_knowledge_graph.py --input $(INPUT_CSV) --output $(OUTPUT_KG) $(if $(HEADER),--header,)

# Build KG from ChEMBL
build-chembl-kg:
ifndef INPUT_CHEMBL
	$(error INPUT_CHEMBL required: make build-chembl-kg INPUT_CHEMBL=./data/chembl_drugs/chembl_34_chemreps.txt OUTPUT_KG=./data/chembl_kg.json MAX_COMPOUNDS=1000)
endif
ifndef OUTPUT_KG
	$(error OUTPUT_KG required: make build-chembl-kg INPUT_CHEMBL=... OUTPUT_KG=...)
endif
	@python scripts/build_chembl_kg.py --input $(INPUT_CHEMBL) --output $(OUTPUT_KG) --max-compounds $(or $(MAX_COMPOUNDS),1000)

# Install the package in development mode
install-dev:
	@pip install -e .

# Clean up downloaded data (keep the directory)
clean:
	@find $(DATA_DIR) -type f \( -name "*.gz" -o -name "*.zip" -o -name "*.tar" \) -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -name "*.pyc" -delete

.PHONY: list-datasets download-all download-% import-pdfs build-kg build-chembl-kg install-dev clean
