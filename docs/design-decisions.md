# Design decisions

This document exists to be interrogated. Each entry names a decision that is
visible in the code, the alternative it rejected, and the cost it accepted.

## 1. The value curve is the model

An `AllocationItem` carries `values`, a tuple where `values[k]` is the *total*
value of giving that item `k` units. Not a marginal gain, not a rate, not a
function.

Rejected alternative: a value function plus a shape parameter. That would be
compact but would smuggle an assumption about the shape, and the point of this
model is to accept arbitrary shapes, including convex ones where greedy fails.

Cost accepted: the caller must supply a full curve, and the curve's length caps
the allocation. `max_units` must fit inside it, which is checked at
construction ([`src/allocdp/models.py`](../src/allocdp/models.py)).

## 2. The curve must start at zero

`__post_init__` rejects a curve whose first entry is non-zero. Allocating
nothing must be worth nothing, or "value" and "value above a baseline" get
mixed and the objective stops being comparable across items.

## 3. Invalid input is rejected at construction, not at solve time

Empty name, empty curve, negative `min_units`, `max_units` outside the curve,
non-finite values, a non-zero start, duplicate work between `min_units` and the
budget: all raise `ValueError` when the dataclass is built. `AllocationProblem`
additionally rejects a negative budget, an empty item set, and minimums whose
sum exceeds the budget.

Rejected alternative: validate inside the solver. Then two solvers have to
agree on the rules, and a caller can hold an object that is already impossible.

Consequence worth naming: because the problem-level check guarantees the
minimums fit, the "no allocation satisfies the item bounds" branch inside
`solve_dynamic_programming` is unreachable in practice. It is a guard against a
future relaxation of the constructor, not live behaviour.

## 4. The dynamic program carries the allocation in its state

Each state is `(value, allocation_tuple)` indexed by units spent, so the optimal
allocation is read out directly rather than reconstructed by backtracking
through a parent table.

Rejected alternative: store values only and backtrack. Lower memory, but
reconstruction has to re-derive tie-breaks, and any mismatch between the forward
and backward rules produces a plan that does not match the reported value.

Cost accepted: memory is `O(budget x items)` in tuple storage rather than
`O(budget)`. This is a small-instance explainer, not a large-scale solver.

## 5. Ties are broken deterministically, in both directions consistently

During the sweep, a candidate replaces an incumbent when it is better by more
than `1e-12`, or equal within `1e-12` and lexicographically smaller. The final
selection uses `max(..., key=(value, tuple(-u for u in allocation)))`, which
also prefers the lexicographically smaller allocation.

The two rules agree, which is why repeated runs and the brute-force oracle
return the same plan for equal-valued alternatives.
`test_equal_curves_resolve_deterministically` pins this.

## 6. Greedy is kept as a foil, with its failure case in the test suite

`solve_greedy` takes the largest available marginal gain each step. That is
optimal for concave curves and wrong for convex ones.

Rather than describe that in prose only,
`test_greedy_is_strictly_suboptimal_on_a_convex_curve` builds a curve that pays
nothing for the first unit and a lot for the second, and asserts greedy scores
strictly worse than the exact solver and the oracle.

Rejected alternative: ship only the exact solver. The comparison is the
teaching content, and a baseline that never loses teaches nothing.

Note: `marginal` returns `-inf` at the upper bound, and the greedy loop already
filters items at their bound, so the `isfinite` break inside the loop is
defensive rather than reachable.

## 7. A brute-force oracle is part of the package, not the tests

`brute_force` enumerates the feasible product of ranges. It lives in
[`src/allocdp/solver.py`](../src/allocdp/solver.py) so that a reader can verify
the exact solver against it on their own instance, not only inside the test
suite.

Cost accepted: it is exponential and only usable on small instances. The
docstring says so.

## 8. The trace is produced by the solver that made the decision

The dynamic program emits a per-item trace of units and value; greedy emits a
per-step trace of which item received the unit and what marginal gain justified
it. Each solver reports its own reasoning rather than a shared post-hoc
narrative, so the explanation cannot drift from the algorithm.

## Known weaknesses

1. **Separable objective only.** No interaction terms, no synergies, no
   substitution effects. Real allocation problems usually have them.
2. **One budget dimension.** Two scarce resources would need a different state
   space.
3. **Integer units only.** No fractional allocation and therefore no LP
   relaxation, no duals, and no shadow prices.
4. **No sensitivity analysis.** The report says what the optimum is, not how
   much the budget would have to change to alter the decision.
5. **Memory grows with the budget** because full allocation tuples live in the
   state table (section 4).
6. **Two unreachable defensive branches** are documented in sections 3 and 6
   rather than removed, because the constructor guarantees that makes them dead
   could reasonably be relaxed later.
7. **Benchmark scenarios are self-authored.** Four synthetic cases that check
   the contract and determinism; they are not evidence about any real problem.
8. **The tie-break convention is arbitrary.** Preferring the lexicographically
   smaller allocation is stable and reproducible, but it is not a domain
   preference and a real user may want a different rule.

## Scope

Synthetic curves and budgets only. No client budgets, project names, or
financial data are in this repository, and no output here is a recommendation
about a real allocation decision.
