"""Render historical evidence for review; never a fresh source validation."""

import argparse
import json
from pathlib import Path

from finsight.research.model_evidence import build_model_evidence
from finsight.research.models import from_snapshot
from finsight.research.news import enrich_news
from finsight.research.outcomes import assess
from finsight.research.report import build_report, report_bundle
from finsight.sec import SECError


class ReplayOnly:
    def get(self, *args, **kwargs):
        raise SECError(
            "Replay only: this source is not in the supplied snapshot; no network request made."
        )


def replay(path):
    result = from_snapshot(json.loads(path.read_text()))
    result.limitations.insert(
        0,
        "HISTORICAL REPLAY: retained original retrieval times/cutoff. No fresh network requests or paid model calls. Content selection was rerun locally.",
    )
    enrich_news(ReplayOnly(), result.news, result.documents)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    report, citations = build_report(result)
    (args.output / "report.md").write_text(report)
    (args.output / "research.zip").write_bytes(report_bundle(result))
    (args.output / "model-evidence.json").write_text(
        json.dumps(build_model_evidence(result, citations), indent=2)
    )
    (args.output / "coverage.json").write_text(json.dumps(assess(result), indent=2))
    print(
        json.dumps(
            {
                "ticker": result.company.ticker,
                "cutoff": result.cutoff.isoformat(),
                "outcome": assess(result),
                "citations": len(citations),
                "model_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
