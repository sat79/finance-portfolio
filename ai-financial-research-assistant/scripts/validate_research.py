"""Live evidence, not fixtures. Saves private local artifacts and measured end-to-end timings."""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from finsight.research.identity import find_companies
from finsight.research.outcomes import assess
from finsight.research.report import build_report, report_bundle
from finsight.research.workflow import run_research
from finsight.sec import SECClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("exports/research-validation"))
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Bypass all source caches, including company-name resolution.",
    )
    parser.add_argument(
        "--companies", nargs="+", default=["Apple", "Microsoft", "Kaspi.kz", "NVIDIA"]
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sec = SECClient()
    expected = {
        "Apple": "0000320193",
        "Microsoft": "0000789019",
        "Kaspi.kz": "0001985487",
        "NVIDIA": "0001045810",
    }
    outcomes = []
    end = datetime.now(timezone.utc).date()
    for name in args.companies:
        start = time.perf_counter()
        attempted_at = datetime.now(timezone.utc).isoformat()
        sec.attempts.clear()
        try:
            matches = find_companies(sec, name, refresh=args.refresh)
            company = next(c for c in matches if c.cik == expected[name])
            result = run_research(
                company,
                end - timedelta(days=89),
                end,
                sec=sec,
                refresh=args.refresh,
                progress=lambda stage, r: print(name, stage, r.stages[stage], flush=True),
            )
            report, citations = build_report(result)
            (args.output / f"{company.ticker}-report.md").write_text(report)
            (args.output / f"{company.ticker}-research.zip").write_bytes(report_bundle(result))
            (args.output / f"{company.ticker}-evidence.json").write_text(
                json.dumps(result.serializable(), default=str, indent=2)
            )
            row = {
                "query": name,
                "attempted_at": attempted_at,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "research_cutoff": result.cutoff.isoformat(),
                "cache_policy": "fresh, bypass caches" if args.refresh else "dated cache permitted",
                "source_access": result.access_attempts,
                "outcome": assess(result),
                "document_register": [
                    {
                        "id": d.id,
                        "url": d.url,
                        "period": d.period,
                        "status": d.status,
                        "retrieved_at": d.retrieved_at,
                        "cached": d.cached,
                        "sha256": d.sha256,
                    }
                    for d in result.documents
                ],
                "news_content_read": sum(bool(n.content) for n in result.news),
                "ticker": company.ticker,
                "matched_listings": len(matches),
                "seconds_including_search_and_export": round(time.perf_counter() - start, 2),
                "stage_seconds": result.seconds,
                "documents": len(result.documents),
                "read_documents": sum(d.status == "read" for d in result.documents),
                "news_items": len(result.news),
                "news_stage": result.stages["Recent news"],
                "financial_coverage": result.dataset is not None,
                "citations": len(citations),
                "model_calls": 0,
                "actual_model_cost_usd": 0,
                "limitations": result.limitations,
            }
            row["validation"] = assess(result)["status"].upper()
            outcomes.append(row)
            print(json.dumps(row), flush=True)
        except (ValueError, StopIteration, OSError) as exc:
            outcomes.append(
                {
                    "query": name,
                    "validation": "FAILED",
                    "reason": str(exc),
                    "attempted_at": attempted_at,
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                    "cache_policy": "fresh, bypass caches"
                    if args.refresh
                    else "dated cache permitted",
                    "source_access": list(sec.attempts),
                    "documents": 0,
                    "read_documents": 0,
                    "news_items": 0,
                    "news_coverage": "not attempted: company resolution failed",
                    "financial_coverage": "not attempted: company resolution failed",
                    "model_calls": 0,
                    "actual_model_cost_usd": 0,
                }
            )
    extra = {}
    for query in ["American", "NonexistentPrivateExampleZZZ"]:
        try:
            extra[query] = [
                {"name": c.name, "ticker": c.ticker, "cik": c.cik}
                for c in find_companies(sec, query, refresh=args.refresh)[:10]
            ]
        except (ValueError, OSError) as exc:
            extra[query] = {"validation": "FAILED", "reason": str(exc)}
    (args.output / "summary.json").write_text(
        json.dumps(
            {
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "companies": outcomes,
                "disambiguation_and_unsupported": extra,
            },
            indent=2,
        )
    )
    return int(
        any(row["validation"] != "COMPLETE" for row in outcomes)
        or any(isinstance(value, dict) for value in extra.values())
    )


if __name__ == "__main__":
    raise SystemExit(main())
