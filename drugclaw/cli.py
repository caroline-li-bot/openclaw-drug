#!/usr/bin/env python3
"""
DrugClaw Command Line Interface
"""

import argparse
import sys
import json
import logging
from typing import Optional

from .main_system import DrugClawSystem
from .config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """Setup CLI parser"""
    parser = argparse.ArgumentParser(
        description='DrugClaw - AI-powered drug discovery assistant'
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # list command
    list_parser = subparsers.add_parser('list', help='List available skills and categories')
    
    # doctor command
    doctor_parser = subparsers.add_parser('doctor', help='Check configuration health')
    
    # demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo query')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Run a custom query')
    run_parser.add_argument('--query', '-q', required=True, help='Query text')
    run_parser.add_argument('--key-file', default='navigator_api_keys.json', help='API key file')
    run_parser.add_argument('--thinking-mode', '-m', choices=['simple', 'graph', 'web_only'], 
                           help='Thinking mode')
    run_parser.add_argument('--show-plan', action='store_true', help='Show query analysis plan')
    run_parser.add_argument('--show-evidence', action='store_true', help='Show raw evidence')
    run_parser.add_argument('--save-md-report', action='store_true', help='Save as Markdown report')
    run_parser.add_argument('--debug-agents', action='store_true', help='Debug agent output')
    
    return parser

def list_skills(drugclaw: DrugClawSystem):
    """List available skills"""
    skills = drugclaw.get_available_skills()
    
    print("=== DrugClaw Available Skills ===\n")
    
    total_skills = 0
    for category in sorted(skills.keys()):
        skill_list = skills[category]
        total_skills += len(skill_list)
        print(f"**{category}** ({len(skill_list)}):")
        for skill in sorted(skill_list):
            print(f"  - {skill}")
        print()
    
    print(f"Total: {total_skills} skills in {len(skills)} categories")

def doctor(config: Config):
    """Check configuration health"""
    print("=== DrugClaw Doctor Check ===\n")
    
    if config.is_valid():
        print("✅ API key is configured")
        print(f"   Model: {config.model}")
        print(f"   Base URL: {config.base_url}")
        print("\n✅ Configuration looks good!")
    else:
        print("❌ API key not found or invalid")
        print("\nPlease check your navigator_api_keys.json file")
        print("Example format:")
        print('''
{
  "api_key": "your-api-key-here",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o"
}
        ''')

def run_demo():
    """Run demo query"""
    print("=== DrugClaw Demo ===\n")
    print("Query: What prescribing and safety information is available for metformin?")
    print("\nUsing SIMPLE mode with online labeling resources...\n")

def main():
    """Main CLI entrypoint"""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Load config
    key_file = getattr(args, 'key_file', 'navigator_api_keys.json')
    
    if not hasattr(args, 'key_file'):
        key_file = 'navigator_api_keys.json'
    
    try:
        config = Config.from_file(key_file)
    except FileNotFoundError:
        # Try environment
        config = Config.from_env()
    
    if not config.is_valid():
        print(f"❌ Could not load configuration from {key_file}")
        print("Please create navigator_api_keys.json with your API key")
        sys.exit(1)
    
    drugclaw = DrugClawSystem(config)
    
    if args.command == 'list':
        list_skills(drugclaw)
    elif args.command == 'doctor':
        doctor(config)
    elif args.command == 'demo':
        doctor(config)
        print()
        run_demo()
    elif args.command == 'run':
        if args.show_plan:
            from drugclaw.agent.planner import PlannerAgent
            planner = PlannerAgent()
            analysis = planner.analyze(args.query)
            print("=== Query Analysis Plan ===")
            print(f"Query: {args.query}")
            print(f"Entities: {analysis.entities}")
            print(f"Entity Types: {analysis.entity_types}")
            print(f"Selected Categories: {analysis.selected_categories}")
            print(f"Thinking Mode: {analysis.thinking_mode}")
            print()
        
        result = drugclaw.query(
            args.query,
            thinking_mode=args.thinking_mode
        )
        
        print(result['answer'])
        print()
        print(f"---")
        print(f"Found {result['evidence_count']} evidence pieces from {len(result['sources'])} sources")
        
        if args.show_evidence:
            print("\n=== Raw Evidence ===")
            for i, (source, claim) in enumerate(zip(result['sources'], result['claims'])):
                print(f"{i+1}. [{source}] {claim.get('content', '')[:100]}...")
        
        if args.save_md_report:
            import os
            import hashlib
            query_hash = hashlib.md5(args.query.encode()).hexdigest()[:8]
            output_dir = f"query_logs/{query_hash}"
            os.makedirs(output_dir, exist_ok=True)
            output_path = f"{output_dir}/report.md"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['answer'])
            
            print(f"\nReport saved to: {output_path}")

if __name__ == '__main__':
    main()
