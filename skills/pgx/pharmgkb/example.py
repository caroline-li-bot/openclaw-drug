#!/usr/bin/env python3
"""
Example: Query pharmacogenomic information from PharmGKB
"""

import requests
import json

def get_variant_guidance(gene: str, variant: str, drug: str, api_key: str) -> dict:
    """Get dosing guidance for a gene-variant-drug combination"""
    
    url = f"https://api.pharmgkb.org/v1/data/clinicalAnnotation"
    params = {
        "gene": gene,
        "drug": drug,
        "access_token": api_key
    }
    
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    # Example: CYP2C19 and clopidogrel
    # You need a free API key from PharmGKB
    api_key = "your-api-key-here"
    result = get_variant_guidance("CYP2C19", "*2/*3", "clopidogrel", api_key)
    
    print("PharmGKB guidance for CYP2C19 and clopidogrel:")
    print(json.dumps(result, indent=2))
