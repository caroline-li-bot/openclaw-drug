# ChEMBL - Drug-Target Interaction Skill

## About ChEMBL

ChEMBL is a manually curated database of bioactive molecules with drug-like properties. It contains bioactivity data for drug targets from the literature.

## API Access

This skill uses the `chembl_webresource_client` Python package to access the ChEMBL API.

### Installation

```bash
pip install chembl_webresource_client
```

## Usage

Retrieve drug-target interactions for a given drug or target.

### Example Queries

- "What are the targets of imatinib?"
- "Find compounds that target EGFR"
- "Get bioactivity data for CHEMBL1171"

## Output Format

The skill returns a list of target (or compound) entries with:
- Target name and ChEMBL ID
- Known activity values (IC50, Ki, etc.)
- Target organism
- Target function
