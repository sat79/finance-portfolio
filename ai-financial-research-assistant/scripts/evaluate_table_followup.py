"""Re-evaluate frozen targets against retained original HTML; not a new holdout or live fetch."""

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from finsight.research.tables import extract_tables


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    previous = root / "docs/review-artifacts/2026-10-25-tables/table-checks"
    comparison = json.loads((previous / "comparison.json").read_text())
    frozen = root / "docs/review-artifacts/2026-10-25/unused-disclosure/frozen-result.json"
    assert (
        hashlib.sha256(frozen.read_bytes()).hexdigest()
        == comparison["results"][0]["frozen_original_result"]["sha256"]
    )
    result = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "method": __doc__,
        "original_results_unchanged": True,
        "companies": [],
    }
    with zipfile.ZipFile(previous / "original-html-sources.zip") as archive:
        for name, old in zip(["apple", "msft"], comparison["results"]):
            content = archive.read(name + ".html")
            assert hashlib.sha256(content).hexdigest() == old["source_sha256"]
            tables, notes = extract_tables(content, "text/html")
            if name == "apple":
                targets = []
                for target in old["table_targets"]:
                    table_id, row_id = target["citation"].split(":")[1:]
                    targets.append(
                        {
                            "name": target["target"],
                            "table": int(table_id[1:]),
                            "row": int(row_id[1:]),
                            "old_values": target["values"],
                        }
                    )
            else:
                targets = json.loads((previous / "msft-preregistered.json").read_text())["targets"]
            outcomes = []
            for target in targets:
                table = next((t for t in tables if t["table"] == target["table"]), {})
                row = next(
                    (
                        r
                        for r in table.get("rows", [])
                        if (
                            r["row"] == target["row"]
                            if "row" in target
                            else r["label"] == target["label"]
                        )
                    ),
                    None,
                )
                success = bool(row and row["status"] == "structured")
                if success and "old_values" in target:
                    assert row["values"] == target["old_values"]
                outcomes.append(
                    {
                        "target": target["name"],
                        "success": success,
                        "citation": f"H1:T{table['table']}:R{row['row']}" if success else None,
                        "row": row,
                        "context": table.get("context"),
                        "units": table.get("units"),
                    }
                )
            result["companies"].append(
                {
                    "company": old["company"],
                    "source_sha256": old["source_sha256"],
                    "original_score": "4/8 frozen prose check; 8/8 at a577eef"
                    if name == "apple"
                    else "2/5 at a577eef",
                    "table_targets_passed": sum(o["success"] for o in outcomes),
                    "table_targets_total": len(outcomes),
                    "outcomes": outcomes,
                    "selected_table_ordinals": [t["table"] for t in tables],
                    "notes": notes,
                    "omitted_rows": {
                        str(t["table"]): t.get("omitted_row_labels", []) for t in tables
                    },
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(
        json.dumps(
            [
                {
                    k: c[k]
                    for k in [
                        "company",
                        "original_score",
                        "table_targets_passed",
                        "table_targets_total",
                    ]
                }
                for c in result["companies"]
            ]
        )
    )


if __name__ == "__main__":
    main()
