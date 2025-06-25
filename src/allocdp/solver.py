from __future__ import annotations

import itertools
import math
from typing import Any

from .models import AllocationProblem, AllocationResult


def _value(problem: AllocationProblem, allocation: tuple[int, ...]) -> float:
    return sum(item.value_at(units) for item, units in zip(problem.items, allocation, strict=True))


def solve_dynamic_programming(problem: AllocationProblem) -> AllocationResult:
    """Find the exact integer optimum and retain enough state to explain it."""

    # Each entry is (value, allocation). Keeping the allocation in the state
    # makes reconstruction explicit and deterministic for equal-valued plans.
    states: list[tuple[float, tuple[int, ...]] | None] = [None] * (problem.budget + 1)
    states[0] = (0.0, ())
    for item in problem.items:
        next_states: list[tuple[float, tuple[int, ...]] | None] = [None] * (problem.budget + 1)
        for spent, state in enumerate(states):
            if state is None:
                continue
            previous_value, previous_allocation = state
            for units in range(item.min_units, min(item.upper_bound, problem.budget - spent) + 1):
                total_spent = spent + units
                candidate = (previous_value + item.value_at(units), previous_allocation + (units,))
                incumbent = next_states[total_spent]
                if incumbent is None or candidate[0] > incumbent[0] + 1e-12 or (
                    abs(candidate[0] - incumbent[0]) <= 1e-12 and candidate[1] < incumbent[1]
                ):
                    next_states[total_spent] = candidate
        states = next_states
    feasible = [state for state in states if state is not None]
    if not feasible:
        raise ValueError("no allocation satisfies the item bounds")
    best_value, best_allocation = max(feasible, key=lambda state: (state[0], tuple(-u for u in state[1])))
    spent = sum(best_allocation)
    trace = tuple(
        {"item": item.name, "units": units, "value": item.value_at(units)}
        for item, units in zip(problem.items, best_allocation, strict=True)
    )
    return AllocationResult("dynamic-programming", best_allocation, best_value, spent, trace, optimal=True)


def solve_greedy(problem: AllocationProblem) -> AllocationResult:
    """Allocate the largest available marginal gain at each step."""

    allocation = [item.min_units for item in problem.items]
    spent = sum(allocation)
    trace: list[dict[str, Any]] = []
    while spent < problem.budget:
        choices = [
            (item.marginal(units), index, item)
            for index, (item, units) in enumerate(zip(problem.items, allocation, strict=True))
            if units < item.upper_bound
        ]
        if not choices:
            break
        marginal, index, item = max(choices, key=lambda choice: (choice[0], -choice[1]))
        if not math.isfinite(marginal):
            break
        allocation[index] += 1
        spent += 1
        trace.append({"item": item.name, "unit": allocation[index], "marginal_value": marginal})
    allocation_tuple = tuple(allocation)
    return AllocationResult(
        "greedy", allocation_tuple, _value(problem, allocation_tuple), spent, tuple(trace), optimal=False
    )


def brute_force(problem: AllocationProblem) -> AllocationResult:
    """Small-instance oracle used by tests and educational notebooks."""

    ranges = [range(item.min_units, item.upper_bound + 1) for item in problem.items]
    candidates = [allocation for allocation in itertools.product(*ranges) if sum(allocation) <= problem.budget]
    if not candidates:
        raise ValueError("no feasible allocation")
    allocation = max(candidates, key=lambda candidate: (_value(problem, candidate), tuple(-u for u in candidate)))
    return AllocationResult("brute-force", allocation, _value(problem, allocation), sum(allocation), optimal=True)
