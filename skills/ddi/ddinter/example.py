#!/usr/bin/env python3
"""
Example: Check drug-drug interactions from DDInter
"""

import requests
import json

def check_interaction(drug1: str, drug2: str) -> dict:
    """Check interaction between two drugs"""
    
    # DDInter API endpoint
    url = "http://www.compbio.cn/ddinter/api/search"
    
    payload = {
        "drugA": drug1,
        "drugB": drug2
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    return data

if __name__ == "__main__":
    # Example: warfarin and ibuprofen
    result = check_interaction("warfarin", "ibuprofen")
    
    print(f"Interaction check between warfarin and ibuprofen:")
    print(json.dumps(result, indent=2))
