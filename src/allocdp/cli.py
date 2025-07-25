from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import AllocationItem, AllocationProblem
from .report import write_report
from .solver import solve_dynamic_programming, solve_greedy


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="allocdp", description="Compare exact and greedy resource allocation.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="Run a synthetic diminishing-return allocation")
    demo.add_argument("--budget", type=int, default=18)
    demo.add_argument("--output-dir", type=Path, default=Path("outputs/demo"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "demo":
        problem = AllocationProblem(
            budget=args.budget,
            items=(
                AllocationItem("reliability", (0, 8, 14, 19, 23, 26, 28, 29)),
                AllocationItem("discovery", (0, 11, 18, 23, 27, 30, 32), min_units=1),
                AllocationItem("delivery", (0, 7, 13, 18, 22, 25, 27, 28, 29)),
            ),
        )
        exact = solve_dynamic_programming(problem)
        greedy = solve_greedy(problem)
        artifacts = write_report(problem, [exact, greedy], args.output_dir)
        payload = {
            "problem": problem.as_dict(),
            "exact": exact.as_dict(),
            "greedy": greedy.as_dict(),
            "artifacts": artifacts,
        }
        print(json.dumps(payload, indent=2))
        return 0
    return 2
