"""Live evidence, not fixtures. Saves private local artifacts and measured end-to-end timings."""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from finsight.research.identity import find_companies
from finsight.research.report import build_report, report_bundle
from finsight.research.workflow import run_research
from finsight.sec import SECClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("exports/research-validation"))
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh document/news/financial evidence; directory uses its dated cache.",
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
        try:
            matches = find_companies(sec, name)
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
            if not any(d.kind == "annual" and d.status == "read" for d in result.documents):
                row["validation"] = "INCOMPLETE: annual document unavailable"
            elif company.supported and result.dataset is None:
                row["validation"] = "INCOMPLETE: supported financial extraction failed"
            elif result.stages["Recent news"] != "completed":
                row["validation"] = "INCOMPLETE: news retrieval failed"
            else:
                row["validation"] = "REPORT_CREATED; inspect source and news limitations"
            outcomes.append(row)
            print(json.dumps(row), flush=True)
        except (ValueError, StopIteration, OSError) as exc:
            outcomes.append({"query": name, "validation": "FAILED", "reason": str(exc)})
    extra = {}
    for query in ["American", "NonexistentPrivateExampleZZZ"]:
        try:
            extra[query] = [
                {"name": c.name, "ticker": c.ticker, "cik": c.cik}
                for c in find_companies(sec, query)[:10]
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
        any(not row["validation"].startswith("REPORT_CREATED") for row in outcomes)
        or any(isinstance(value, dict) for value in extra.values())
    )


if __name__ == "__main__":
    raise SystemExit(main())
