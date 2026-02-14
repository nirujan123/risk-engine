import argparse
from pathlib import Path

from .config import load_config
from .run import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(prog="risk_engine")

    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run the risk engine pipeline")
    run_p.add_argument(
        "--config",
        required=True,
        help="Path to YAML config, e.g. configs/demo.yaml",
    )

    args = parser.parse_args()

    if args.command == "run":
        cfg = load_config(Path(args.config))
        run_dir = run_pipeline(cfg)
        print(f"Run saved to: {run_dir}")
        return 0

    return 1
