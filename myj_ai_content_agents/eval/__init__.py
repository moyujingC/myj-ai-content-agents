"""Eval 入口."""

from __future__ import annotations

from myj_ai_content_agents.eval.checks import DEFAULT_CHECKS
from myj_ai_content_agents.models import ContentUnit


def evaluate(unit: ContentUnit, checks: list | None = None) -> dict:
    """执行 Eval 检查."""
    checks = checks or DEFAULT_CHECKS
    results = []
    all_passed = True
    for check in checks:
        ok, msg = check(unit)
        results.append({"check": check.__name__, "passed": ok, "message": msg})
        if not ok:
            all_passed = False
    return {
        "passed": all_passed,
        "total": len(results),
        "failed": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
