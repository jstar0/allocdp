"""Failure paths and edge cases.

The happy path is covered in test_solver.py. These tests pin the behaviour a
reviewer is most likely to probe: what the model rejects, what it does at the
boundaries, and where the greedy baseline is provably worse than the exact
solver rather than merely slower.
"""

from __future__ import annotations

import pytest

from allocdp import AllocationItem, AllocationProblem, brute_force, solve_dynamic_programming, solve_greedy


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"name": "  ", "values": (0, 1)}, "needs a name"),
        ({"name": "a", "values": ()}, "needs a name"),
        ({"name": "a", "values": (0, 1), "min_units": -1}, "cannot be negative"),
        ({"name": "a", "values": (0, 1), "max_units": 5}, "must fit inside"),
        ({"name": "a", "values": (0, 1), "min_units": 1, "max_units": 0}, "must fit inside"),
        ({"name": "a", "values": (0, float("inf"))}, "finite numbers"),
        ({"name": "a", "values": (0, float("nan"))}, "finite numbers"),
        ({"name": "a", "values": (2, 4)}, "must start at zero"),
    ],
)
def test_invalid_item_is_rejected(kwargs: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        AllocationItem(**kwargs)


def test_negative_budget_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        AllocationProblem(-1, (AllocationItem("a", (0, 1)),))


def test_empty_item_set_is_rejected() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        AllocationProblem(3, ())


def test_minimums_above_budget_are_rejected() -> None:
    items = (
        AllocationItem("a", (0, 1, 2), min_units=2),
        AllocationItem("b", (0, 1, 2), min_units=2),
    )
    with pytest.raises(ValueError, match="exceed the budget"):
        AllocationProblem(3, items)


def test_value_outside_bounds_is_rejected() -> None:
    item = AllocationItem("a", (0, 3, 5), max_units=1)
    assert item.value_at(1) == 3
    with pytest.raises(ValueError, match="outside its bounds"):
        item.value_at(2)
    with pytest.raises(ValueError, match="outside its bounds"):
        item.value_at(-1)


def test_marginal_at_upper_bound_is_negative_infinity() -> None:
    item = AllocationItem("a", (0, 3, 5), max_units=1)
    assert item.marginal(0) == 3
    assert item.marginal(1) == float("-inf")


def test_zero_budget_allocates_nothing() -> None:
    problem = AllocationProblem(0, (AllocationItem("a", (0, 9)), AllocationItem("b", (0, 4))))
    exact = solve_dynamic_programming(problem)
    greedy = solve_greedy(problem)
    assert exact.allocation == (0, 0)
    assert exact.value == 0
    assert greedy.allocation == (0, 0)
    assert greedy.trace == ()


def test_budget_beyond_total_capacity_stops_at_upper_bounds() -> None:
    problem = AllocationProblem(20, (AllocationItem("a", (0, 4, 6)), AllocationItem("b", (0, 3))))
    exact = solve_dynamic_programming(problem)
    assert exact.allocation == (2, 1)
    assert exact.budget_used == 3 < problem.budget

    greedy = solve_greedy(problem)
    assert greedy.allocation == (2, 1)
    assert greedy.budget_used == 3


def test_greedy_is_strictly_suboptimal_on_a_convex_curve() -> None:
    """Greedy assumes diminishing returns; a convex curve breaks that assumption.

    Item "step" pays nothing for the first unit and a lot for the second, so the
    largest immediate marginal gain leads greedy away from the optimum.
    """
    problem = AllocationProblem(
        budget=2,
        items=(AllocationItem("step", (0, 0, 10)), AllocationItem("flat", (0, 1, 2))),
    )
    exact = solve_dynamic_programming(problem)
    greedy = solve_greedy(problem)
    oracle = brute_force(problem)

    assert exact.allocation == oracle.allocation == (2, 0)
    assert exact.value == 10
    assert greedy.value < exact.value
    assert greedy.optimal is False and exact.optimal is True


def test_equal_curves_resolve_deterministically() -> None:
    problem = AllocationProblem(2, (AllocationItem("a", (0, 5, 8)), AllocationItem("b", (0, 5, 8))))
    first = solve_dynamic_programming(problem)
    second = solve_dynamic_programming(problem)
    assert first.allocation == second.allocation
    assert first.allocation == brute_force(problem).allocation


def test_forced_minimums_are_respected_by_both_solvers() -> None:
    problem = AllocationProblem(
        budget=4,
        items=(
            AllocationItem("floor", (0, 1, 2, 3), min_units=2),
            AllocationItem("free", (0, 9, 10, 11)),
        ),
    )
    exact = solve_dynamic_programming(problem)
    greedy = solve_greedy(problem)
    assert exact.allocation[0] >= 2
    assert greedy.allocation[0] >= 2
    assert sum(exact.allocation) <= 4
    assert sum(greedy.allocation) <= 4
