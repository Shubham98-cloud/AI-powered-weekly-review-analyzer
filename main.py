import argparse
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.orchestrator import run_full_agent

def parse_args():
    parser = argparse.ArgumentParser(description="Weekly Product Review Pulse AI Agent - v1.0")
    parser.add_argument("--product", type=str, help="Run only for a specific product (e.g. Groww)")
    parser.add_argument("--week", type=str, help="Force a specific ISO week (e.g. 2026-W17)")
    parser.add_argument("--dry-run", action="store_true", help="Process data but do not deliver or log to audit store")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        run_full_agent(product=args.product, week=args.week, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)
