from allocdp.benchmark import run_benchmark


def test_benchmark_runs_multiple_constraints_and_oracles() -> None:
    result = run_benchmark()
    assert result["case_count"] == 4
    assert result["all_oracles_match"] is True


def test_exact_solution_is_never_worse_than_greedy() -> None:
    result = run_benchmark()
    assert all(case["exact_value"] >= case["greedy_value"] for case in result["cases"])
    assert result["total_greedy_gap"] >= 0
    assert result["cases"][-1]["greedy_gap"] > 0


def test_allocations_respect_budget() -> None:
    result = run_benchmark()
    assert all(case["exact_budget_used"] <= case["budget"] for case in result["cases"])
    assert all(case["greedy_budget_used"] <= case["budget"] for case in result["cases"])


def test_benchmark_is_deterministic() -> None:
    assert run_benchmark() == run_benchmark()
