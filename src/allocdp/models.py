from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AllocationItem:
    """One project with a value curve indexed by allocated integer units."""

    name: str
    values: tuple[float, ...]
    min_units: int = 0
    max_units: int | None = None

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.values:
            raise ValueError("an item needs a name and at least one value point")
        if self.min_units < 0:
            raise ValueError("min_units cannot be negative")
        maximum = self.max_units if self.max_units is not None else len(self.values) - 1
        if maximum < self.min_units or maximum >= len(self.values):
            raise ValueError("max_units must fit inside the value curve")
        if any(not math.isfinite(float(value)) for value in self.values):
            raise ValueError("value curves must contain finite numbers")
        if abs(float(self.values[0])) > 1e-9:
            raise ValueError("value curve must start at zero")

    @property
    def upper_bound(self) -> int:
        return self.max_units if self.max_units is not None else len(self.values) - 1

    def value_at(self, units: int) -> float:
        if units < 0 or units > self.upper_bound:
            raise ValueError(f"{self.name} allocation is outside its bounds")
        return float(self.values[units])

    def marginal(self, units: int) -> float:
        if units >= self.upper_bound:
            return float("-inf")
        return self.value_at(units + 1) - self.value_at(units)


@dataclass(frozen=True, slots=True)
class AllocationProblem:
    budget: int
    items: tuple[AllocationItem, ...]

    def __post_init__(self) -> None:
        if self.budget < 0 or not self.items:
            raise ValueError("budget must be non-negative and items cannot be empty")
        if sum(item.min_units for item in self.items) > self.budget:
            raise ValueError("minimum allocations exceed the budget")

    def as_dict(self) -> dict[str, Any]:
        return {
            "budget": self.budget,
            "items": [
                {
                    "name": item.name,
                    "values": list(item.values),
                    "min_units": item.min_units,
                    "max_units": item.upper_bound,
                }
                for item in self.items
            ],
        }


@dataclass(frozen=True, slots=True)
class AllocationResult:
    method: str
    allocation: tuple[int, ...]
    value: float
    budget_used: int
    trace: tuple[dict[str, Any], ...] = ()
    optimal: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "allocation": list(self.allocation),
            "value": round(self.value, 8),
            "budget_used": self.budget_used,
            "optimal": self.optimal,
            "trace": list(self.trace),
        }
