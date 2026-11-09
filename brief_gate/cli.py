import argparse
import sys
import json
from pathlib import Path
from .evaluator import evaluate_asset
from . import __version__

def main():
    parser = argparse.ArgumentParser(
        prog="brief-gate",
        description="Deterministic quality gate for AI marketing copy and creative assets."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    eval_parser = subparsers.add_parser("evaluate", help="Evaluate an asset against a brief")
    eval_parser.add_argument("--brief", "-b", required=True, help="Path to brief JSON file")
    eval_parser.add_argument("--asset", "-a", required=True, help="Path to generated asset file (markdown/txt)")
    eval_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "evaluate":
        brief_path = Path(args.brief)
        asset_path = Path(args.asset)

        if not brief_path.exists():
            sys.stderr.write(f"Error: Brief file not found: {brief_path}\n")
            sys.exit(1)

        if not asset_path.exists():
            sys.stderr.write(f"Error: Asset file not found: {asset_path}\n")
            sys.exit(1)

        with open(brief_path, "r", encoding="utf-8") as bf:
            brief_data = json.load(bf)

        with open(asset_path, "r", encoding="utf-8") as af:
            asset_content = af.read()

        result = evaluate_asset(brief_data, asset_content)

        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(result.render_markdown())

        # Exit code reflects gate status: 0 for PASS, 1 for FIX, 2 for BLOCK
        if result.verdict == "PASS":
            sys.exit(0)
        elif result.verdict == "FIX":
            sys.exit(1)
        else:
            sys.exit(2)

if __name__ == "__main__":
    main()
