"""AllocDP: exact and baseline resource-allocation experiments."""

from .models import AllocationItem, AllocationProblem, AllocationResult
from .solver import brute_force, solve_dynamic_programming, solve_greedy

__version__ = "0.1.0"

__all__ = [
    "AllocationItem",
    "AllocationProblem",
    "AllocationResult",
    "__version__",
    "brute_force",
    "solve_dynamic_programming",
    "solve_greedy",
]
