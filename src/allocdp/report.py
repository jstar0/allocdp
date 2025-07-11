from __future__ import annotations

import html
import json
from pathlib import Path

from .models import AllocationProblem, AllocationResult


def write_report(problem: AllocationProblem, results: list[AllocationResult], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {"problem": problem.as_dict(), "results": [result.as_dict() for result in results]}
    json_path = output_dir / "report.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = "".join(
        f"<tr><td>{html.escape(result.method)}</td><td>{result.value:.3f}</td><td>{list(result.allocation)}</td><td>{result.budget_used}</td><td>{'yes' if result.optimal else 'no'}</td></tr>"
        for result in results
    )
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AllocDP report</title><style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:40px auto;padding:0 20px;color:#172033}}.card{{border:1px solid #dbe3ef;border-radius:12px;padding:16px;margin:16px 0;background:#fff}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #e8edf4}}th{{background:#f1f5fa}}code{{white-space:pre-wrap}}</style></head><body><h1>AllocDP allocation report</h1><p>Budget: <strong>{problem.budget}</strong> units. Exact dynamic programming and a marginal-gain baseline are shown side by side.</p><div class="card"><table><thead><tr><th>Method</th><th>Value</th><th>Allocation</th><th>Used</th><th>Optimal</th></tr></thead><tbody>{rows}</tbody></table></div><div class="card"><h2>Problem manifest</h2><code>{html.escape(json.dumps(problem.as_dict(), ensure_ascii=False, indent=2))}</code></div></body></html>"""
    html_path = output_dir / "report.html"
    html_path.write_text(page, encoding="utf-8")
    return {"json": str(json_path), "html": str(html_path)}
