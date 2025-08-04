from __future__ import annotations

from typing import Any

from .models import AllocationItem, AllocationProblem
from .solver import brute_force, solve_dynamic_programming, solve_greedy


def _case(name: str, budget: int, items: tuple[AllocationItem, ...]) -> dict[str, Any]:
    problem = AllocationProblem(budget, items)
    exact = solve_dynamic_programming(problem)
    oracle = brute_force(problem)
    greedy = solve_greedy(problem)
    return {
        "name": name,
        "budget": budget,
        "item_count": len(items),
        "exact_value": round(exact.value, 8),
        "greedy_value": round(greedy.value, 8),
        "greedy_gap": round(exact.value - greedy.value, 8),
        "exact_allocation": list(exact.allocation),
        "greedy_allocation": list(greedy.allocation),
        "oracle_matches": exact.allocation == oracle.allocation and exact.value == oracle.value,
        "exact_budget_used": exact.budget_used,
        "greedy_budget_used": greedy.budget_used,
    }


def run_benchmark() -> dict[str, Any]:
    cases = [
        _case(
            "diminishing-returns",
            12,
            (
                AllocationItem("reliability", (0, 8, 14, 19, 23, 26, 28)),
                AllocationItem("discovery", (0, 11, 18, 23, 27, 30)),
                AllocationItem("delivery", (0, 7, 13, 18, 22, 25, 27)),
            ),
        ),
        _case(
            "minimum-constrained",
            10,
            (
                AllocationItem("research", (0, 5, 9, 12, 14, 15), min_units=2),
                AllocationItem("operations", (0, 4, 7, 9, 10)),
                AllocationItem("support", (0, 6, 10, 13, 15)),
            ),
        ),
        _case(
            "wide-frontier",
            18,
            tuple(
                AllocationItem(
                    f"workstream-{index}",
                    (0, 5 + index, 9 + index, 12 + index, 14 + index, 15 + index),
                )
                for index in range(5)
            ),
        ),
        _case(
            "non-concave-baseline",
            3,
            (
                AllocationItem("steady", (0, 50, 51, 52)),
                AllocationItem("spike", (0, 1, 1, 100)),
            ),
        ),
    ]
    return {
        "benchmark_version": 1,
        "case_count": len(cases),
        "cases": cases,
        "all_oracles_match": all(case["oracle_matches"] for case in cases),
        "total_greedy_gap": round(sum(case["greedy_gap"] for case in cases), 8),
    }
