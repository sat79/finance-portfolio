"""Paired selection evaluation on identical evidence, not a new live-source run.

The named review targets are a small hand-reviewed benchmark, not application rules
or a statistical estimate of materiality/semantic accuracy.
"""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from finsight.research.evidence import recent_evidence
from finsight.research.model_evidence import build_model_evidence
from finsight.research.models import from_snapshot
from finsight.research.report import build_report, report_bundle

TARGETS = {
    "KSPI": {
        "E7:B24": "consolidated quarterly result",
        "E7:B9": "volume/GMV driver",
        "E7:B74": "monetization/constant-currency driver (same measures as memo B11)",
        "E7:B19": "funding-cost explanation",
        "E5:B2151": "Stage 3 restructured-loan stock",
    },
    "AAPL": {
        "E7:B6": "quarterly results and tariff qualifiers",
        "D2:B624": "product margin/mix and tariff explanation",
    },
    "MSFT": {
        "E5:B6": "short reported/constant-currency revenue bullet",
        "E5:B10": "GAAP versus non-GAAP income",
        "E5:B15": "discrete EPS items",
        "E5:B72": "cloud segment driver",
    },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for ticker, targets in TARGETS.items():
        raw = (args.baseline / f"{ticker}-evidence.json").read_bytes()
        research = from_snapshot(json.loads(raw))
        with zipfile.ZipFile(args.baseline / f"{ticker}-research.zip") as archive:
            before = json.loads(archive.read("citations.json"))
            baseline_payload = json.loads(archive.read("model-evidence.json"))
        report, citations = build_report(research)
        model = build_model_evidence(research, citations)
        selected = {
            key
            for s in recent_evidence(research.documents)
            for key in [f"{s['document'].id}:B{r['index'] + 1}" for r in s["records"]]
        }
        source = {
            f"{d.id}:B{i}": p for d in research.documents for i, p in enumerate(d.passages, 1)
        }
        for record in model["recent_disclosures"]:
            for passage in record["passages"]:
                key = passage["citation_id"]
                assert model["citations"][key]["quote"] == source[key].text
                assert model["citations"][key]["locator"] == source[key].locator
        for finding in model["key_findings"]:
            for statement in finding["statements"]:
                assert (
                    statement["text"]
                    in model["citations"][statement["citation_id"]]["support_text"]
                )
            assert all(k in model["citations"] for k in finding["context_citation_ids"])
            assert all(k in model["quantitative_evidence"] for k in finding["calculation_ids"])
        for row in model["selected_financial_observations"] + model["calculations"]:
            assert all(k in model["warning_registry"] for k in row["review_warning_ids"])
        (args.output / f"{ticker}-report.md").write_text(report)
        (args.output / f"{ticker}-research.zip").write_bytes(report_bundle(research))
        (args.output / f"{ticker}-model-evidence.json").write_text(json.dumps(model, indent=2))
        rows.append(
            {
                "ticker": ticker,
                "research_cutoff": research.cutoff.isoformat(),
                "source_snapshot_sha256": hashlib.sha256(raw).hexdigest(),
                "mode": "paired rendering of identical source snapshot; no new fetch",
                "key_findings": len(model["key_findings"]),
                "primary_passages": len(selected),
                "recent_unique_citations": len(
                    {p["citation_id"] for d in model["recent_disclosures"] for p in d["passages"]}
                ),
                "model_bytes_before": len(json.dumps(baseline_payload).encode()),
                "model_bytes_after": len(json.dumps(model).encode()),
                "targets": [
                    {
                        "id": key,
                        "description": description,
                        "before_in_report_and_payload": key in before
                        and key in baseline_payload["citations"],
                        "after_in_report_and_payload": key in citations
                        and key in model["citations"],
                        "after_selected_primary": key in selected,
                        "quote": source[key].text,
                    }
                    for key, description in targets.items()
                ],
                "coverage": model["coverage"],
            }
        )
    (args.output / "evaluation.json").write_text(json.dumps(rows, indent=2))
    print(
        json.dumps(
            [
                {
                    k: r[k]
                    for k in [
                        "ticker",
                        "key_findings",
                        "primary_passages",
                        "recent_unique_citations",
                        "model_bytes_before",
                        "model_bytes_after",
                    ]
                }
                for r in rows
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
