#!/usr/bin/env python3
"""
Deterministic retrieval from DDInter - can be used as fallback
Usage: python retrieve.py drugA drugB [...]
"""

import sys
import requests
import json

def check_interactions(drugs: list):
    """Check interactions between a list of drugs"""
    results = []
    
    # Check all pairwise combinations
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            drugA = drugs[i]
            drugB = drugs[j]
            
            url = "http://www.compbio.cn/ddinter/api/search"
            payload = {"drugA": drugA, "drugB": drugB}
            
            try:
                response = requests.post(url, json=payload, timeout=10)
                data = response.json()
                
                if data.get('interaction', False):
                    severity = data.get('level', 'Unknown')
                    results.append({
                        'drugA': drugA,
                        'drugB': drugB,
                        'interaction': True,
                        'severity': severity
                    })
                else:
                    results.append({
                        'drugA': drugA,
                        'drugB': drugB,
                        'interaction': False
                    })
            except Exception as e:
                results.append({
                    'drugA': drugA,
                    'drugB': drugB,
                    'error': str(e)
                })
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python retrieve.py drugA drugB [drugC ...]")
        print("Checks pairwise interactions between all drugs")
        sys.exit(1)
    
    drugs = sys.argv[1:]
    results = check_interactions(drugs)
    
    print(f"\n=== Drug-Drug Interaction Check ===\n")
    for res in results:
        drugA = res['drugA']
        drugB = res['drugB']
        
        if 'error' in res:
            print(f"❌ {drugA} + {drugB}: Error - {res['error']}")
        elif res['interaction']:
            severity = res.get('severity', 'Unknown')
            print(f"⚠️  {drugA} + {drugB}: Interaction detected, severity: {severity}")
        else:
            print(f"✅ {drugA} + {drugB}: No known interaction found")
