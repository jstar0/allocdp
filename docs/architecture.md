# AllocDP architecture

`models.py` validates value curves and bounds. `solver.py` contains the exact DP, a greedy marginal baseline, and a tiny brute-force oracle for tests. The DP state stores both value and the partial allocation, which makes tie-breaking deterministic and reconstruction auditable. `report.py` serializes the problem and all methods to JSON/HTML; the CLI only assembles a synthetic public fixture.
