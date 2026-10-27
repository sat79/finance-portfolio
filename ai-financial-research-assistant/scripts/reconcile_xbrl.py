"""Recheck the frozen real-company sample against separately downloaded SEC XBRL instances.

This deliberately does not import the application's CompanyFacts parser or calculations.
Download the filing_xml_url values in tests/fixtures/reconciled_companies.json as
AAPL-instance.xml, MSFT-instance.xml and KSPI-instance.xml, then pass their directory with --filings.
"""

import argparse
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS = {"x": "http://www.xbrl.org/2003/instance"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--filings", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("exports/reconciliation.csv"))
    args = parser.parse_args()
    evidence = json.loads((ROOT / "tests/fixtures/reconciled_companies.json").read_text())
    comparisons = []
    for company in evidence:
        raw = (args.filings / f"{company['ticker']}-instance.xml").read_bytes()
        if len(raw) > 25 * 1024 * 1024:
            raise ValueError("XBRL input exceeds 25 MiB.")
        source_hash = hashlib.sha256(raw).hexdigest()
        if source_hash != company["dataset"]["source_hashes"][company["filing_xml_url"]]:
            raise ValueError("Source hash differs from the reviewed filing instance.")
        root = ET.fromstring(raw)
        contexts = {e.attrib["id"]: e for e in root.findall("x:context", NS)}
        units = {e.attrib["id"]: e for e in root.findall("x:unit", NS)}
        for fact in company["dataset"]["observations"]:
            matches = []
            tag = fact["concept"].split(":", 1)[1]
            for element in root:
                namespace = (
                    "xbrl.ifrs.org"
                    if fact["concept"].startswith("ifrs-full:")
                    else "fasb.org/us-gaap"
                )
                if not element.tag.endswith("}" + tag) or namespace not in element.tag:
                    continue
                context = contexts[element.attrib["contextRef"]]
                if (
                    context.find("x:entity/x:segment", NS) is not None
                    or context.find("x:scenario", NS) is not None
                ):
                    continue
                if context.findtext("x:period/x:startDate", namespaces=NS) != fact["start"]:
                    continue
                if context.findtext("x:period/x:endDate", namespaces=NS) != fact["end"]:
                    continue
                unit = units[element.attrib["unitRef"]]
                if unit.findtext("x:measure", namespaces=NS) not in (
                    f"iso4217:{fact['currency']}",
                    fact["currency"],
                ):
                    continue
                matches.append((Decimal(element.text), element.attrib["contextRef"]))
            values = {value for value, _ in matches}
            if len(values) != 1:
                raise ValueError(
                    f"Ambiguous or missing source: {company['ticker']} {fact['end']} {tag}"
                )
            expected = values.pop()
            difference = Decimal(fact["value"]) - expected
            if difference:
                raise ValueError(f"Reconciliation failed: {company['ticker']} {fact['end']} {tag}")
            comparisons.append(
                {
                    "ticker": company["ticker"],
                    "cik": fact["cik"],
                    "fiscal_year": fact["fiscal_year"],
                    "period_start": fact["start"],
                    "period_end": fact["end"],
                    "metric": fact["metric"],
                    "app_value": fact["value"],
                    "independent_xbrl_value": str(expected),
                    "difference": str(difference),
                    "currency": fact["currency"],
                    "concept": tag,
                    "accession": fact["accession"],
                    "source_url": company["filing_xml_url"],
                    "context_id": matches[0][1],
                    "source_sha256": source_hash,
                    "status": "MATCH",
                    "notes": "Compared to standalone filing XBRL, consolidated annual context and reported currency unit; not an independent audit.",
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparisons[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(comparisons)
    print(
        f"PASS: {len(comparisons)} observations reconciled to the frozen official filing instances."
    )


if __name__ == "__main__":
    main()
