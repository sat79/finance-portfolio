"""Attempt real SEC integration and export evidence; never marks independent reconciliation complete."""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from finsight.exports import csv_bundle
from finsight.financials import calculate
from finsight.models import Metric
from finsight.sec import SUPPORTED, SECClient, SECError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("exports/live-validation"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    outcomes = []
    evidence = []
    for ticker in SUPPORTED:
        try:
            data = SECClient().load(ticker, refresh=True)
            if len(data.periods) < 3:
                raise SECError("Fewer than three unambiguous annual periods.")
            for period in data.periods[-3:]:
                required = (
                    {
                        Metric.REVENUE,
                        Metric.NET_INCOME,
                        Metric.OPERATING_CASH_FLOW,
                        Metric.INVESTMENT_PURCHASES,
                        Metric.PARENT_NET_INCOME,
                    }
                    if data.financial_group
                    else {
                        Metric.REVENUE,
                        Metric.OPERATING_PROFIT,
                        Metric.OPERATING_CASH_FLOW,
                        Metric.CAPEX,
                    }
                )
                available = {f.metric for f in data.selected if f.end == period.end}
                if not required <= available:
                    raise SECError(
                        f"{period.label}: required reconciliation metrics missing or ambiguous."
                    )
            (args.output / f"{ticker}-dataset.json").write_text(data.model_dump_json(indent=2))
            (args.output / f"{ticker}-analysis.zip").write_bytes(csv_bundle(data, calculate(data)))
            for fact in data.selected:
                if fact.end not in {p.end for p in data.periods[-3:]}:
                    continue
                evidence.append(
                    {
                        "ticker": ticker,
                        "fiscal_year": fact.fiscal_year,
                        "period_end": fact.end,
                        "metric": fact.metric.value,
                        "app_value": str(fact.value),
                        "currency": fact.currency,
                        "concept": fact.concept,
                        "accession": fact.accession,
                        "source_url": fact.source_url,
                        "independent_value": "",
                        "difference": "",
                        "review_status": "PENDING_MANUAL_RECONCILIATION",
                        "notes": "Open the actual filing and verify the statement definition, period and units.",
                    }
                )
            outcomes.append(
                {
                    "ticker": ticker,
                    "status": "RETRIEVAL_PASSED_RECONCILIATION_PENDING",
                    "periods": len(data.periods),
                    "warnings": len(data.warnings),
                }
            )
        except (SECError, ValueError) as exc:
            outcomes.append({"ticker": ticker, "status": "BLOCKED_OR_FAILED", "reason": str(exc)})
    summary = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "outcomes": outcomes,
        "independent_reconciliation_complete": False,
    }
    (args.output / "status.json").write_text(json.dumps(summary, indent=2) + "\n")
    if evidence:
        with (args.output / "reconciliation-to-review.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(evidence[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(evidence)
    print(json.dumps(summary, indent=2))
    return 1 if any(x["status"] == "BLOCKED_OR_FAILED" for x in outcomes) else 0


if __name__ == "__main__":
    sys.exit(main())
