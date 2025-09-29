import pytest

from allocdp import AllocationItem, AllocationProblem, brute_force, solve_dynamic_programming, solve_greedy


def _problem() -> AllocationProblem:
    return AllocationProblem(
        budget=5,
        items=(AllocationItem("a", (0, 7, 10, 12)), AllocationItem("b", (0, 5, 9, 11))),
    )


def test_dynamic_programming_matches_oracle() -> None:
    problem = _problem()
    exact = solve_dynamic_programming(problem)
    oracle = brute_force(problem)
    assert exact.allocation == oracle.allocation
    assert exact.value == oracle.value
    assert exact.optimal


def test_greedy_is_feasible_and_trace_is_replayable() -> None:
    result = solve_greedy(_problem())
    assert sum(result.allocation) <= 5
    assert result.value >= 0
    assert len(result.trace) == sum(result.allocation)


def test_bounds_are_enforced() -> None:
    problem = AllocationProblem(3, (AllocationItem("a", (0, 3, 5, 6), min_units=2, max_units=2),))
    result = solve_dynamic_programming(problem)
    assert result.allocation == (2,)
    with pytest.raises(ValueError, match="minimum"):
        AllocationProblem(1, (AllocationItem("a", (0, 1, 2), min_units=2),))
