# AllocDP

AllocDP makes resource-allocation decisions explainable. Give each initiative a value curve (the total value after 0, 1, 2, … units), set a budget and optional minimums/maximums, and compare an exact dynamic-programming solution with a greedy marginal-gain baseline.

```bash
uv sync --extra dev
uv run allocdp demo --output-dir outputs/demo
open outputs/demo/report.html
```

The report includes the problem manifest, allocation vector, value, budget usage, and the greedy decision trace. `solve_dynamic_programming` is exact for the integer model; `solve_greedy` is intentionally a baseline, not a universal approximation guarantee.

```python
from allocdp import AllocationItem, AllocationProblem, solve_dynamic_programming

problem = AllocationProblem(
    budget=10,
    items=(AllocationItem("research", (0, 5, 9, 12)), AllocationItem("ops", (0, 4, 7, 9))),
)
result = solve_dynamic_programming(problem)
print(result.allocation, result.value)
```

The implementation is an independent project. It contains no client data, code, prompts, or proprietary value curves.

## Scope and limits

AllocDP is a small exact solver with a deliberately narrow model. The narrowness
is the point, and it is enforced by validation rather than left implicit:

- **The model is separable and integer.** Total value is the sum of per-item
  value curves evaluated at integer unit counts. There are no interactions
  between items, no fractional allocations, no shared side constraints, and no
  precedence.
- **One budget dimension.** A second scarce resource would need a different
  state space; the dynamic program is indexed by spend alone.
- **Value curves must start at zero and be finite**, and `max_units` must fit
  inside the supplied curve. Non-finite values, negative minimums, and minimums
  that exceed the budget are rejected at construction.
- **Greedy is a baseline, not an approximation guarantee.** It is optimal only
  when every curve has diminishing returns; on a convex curve it is provably
  worse, and the test suite pins that case rather than hiding it.
- **Complexity is `O(items x budget x max_units)`** with a full allocation tuple
  kept in each state, so memory grows with the budget. This is built for
  explainability at small scale, not for large instances.
- **Ties are broken deterministically** toward the lexicographically smaller
  allocation, so equal-value plans are stable across runs. That rule is a
  convention, not a domain judgement.
- **Benchmark scenarios are synthetic.** They exercise the solver's contract;
  they are not a claim about any real allocation problem.


## Development

```bash
uv run pytest
uv run --with ruff ruff check src tests
uv lock --check
uv build
uv run allocdp-benchmark --output-dir /tmp/allocdp-benchmark
```

The benchmark compares exact dynamic programming, a greedy marginal-gain
baseline, and a brute-force oracle across diminishing-return, minimum-bound,
wide-frontier, and non-concave synthetic value curves. It writes hash-bound
JSON/CSV/Markdown artifacts and makes the greedy failure mode visible; it is an
algorithmic contract, not a business or resource outcome claim.

MIT licensed; see [LICENSE](LICENSE).
