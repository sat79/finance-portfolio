import csv
import io
import zipfile
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import load_workbook

from finsight.csv_import import ImportError, import_csv
from finsight.exports import csv_bundle, excel_bytes
from finsight.financials import calculate

ROOT = Path(__file__).resolve().parents[1]


def example():
    return (ROOT / "data/examples/valid_synthetic.csv").read_bytes()


def alter(**changes):
    rows = list(csv.DictReader(io.StringIO(example().decode())))
    rows[0].update(changes)
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def test_valid_import_preserves_values_and_labels():
    data = import_csv(example())
    assert data.origin == "csv" and len(data.selected) == 24
    assert all(f.status == "user_provided" and f.source_url is None for f in data.selected)
    assert any(f.value < 0 for f in data.selected)


@pytest.mark.parametrize(
    "changes",
    [
        dict(value="=1+1"),
        dict(value="NaN"),
        dict(value="Infinity"),
        dict(value="1,000"),
        dict(value="1e3"),
        dict(period_end="2024-02-30"),
        dict(period_end="20220630"),
        dict(currency="EUR", unit="EUR"),
        dict(unit="USD millions"),
        dict(cik="abc"),
        dict(schema_version="2"),
        dict(metric="EBITDA"),
        dict(fiscal_year="FY22"),
        dict(source_reference=""),
    ],
)
def test_bad_input_rejected(changes):
    with pytest.raises(ImportError, match="Row"):
        import_csv(alter(**changes))


def test_missing_is_not_zero():
    data = import_csv(alter(value=""))
    assert len(data.selected) == 23
    assert any(w.code == "MISSING_VALUE" for w in data.warnings)


def test_duplicate_and_conflicting_records_rejected():
    raw = example()
    for extra in [
        raw.splitlines(keepends=True)[1],
        raw.splitlines(keepends=True)[1].replace(b"1000", b"9999"),
    ]:
        with pytest.raises(ImportError, match="Duplicate/conflicting"):
            import_csv(raw + extra)


def test_negative_capex_example_rejected():
    with pytest.raises(ImportError, match="positive outflow"):
        import_csv((ROOT / "data/examples/invalid_negative_capex.csv").read_bytes())


@pytest.mark.parametrize(
    "raw", [b"", b"\xff\xfe", b"a,b\n1,2\n", b"\x00", b"x" * (1024 * 1024 + 1)]
)
def test_file_limits_and_schema(raw):
    with pytest.raises(ImportError):
        import_csv(raw)


def test_exports_preserve_linkage_and_metadata(dataset):
    calculations = calculate(dataset)
    bundle = csv_bundle(dataset, calculations)
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        assert set(archive.namelist()) == {
            f"{x}.csv" for x in ["financials", "calculations", "sources", "warnings", "metadata"]
        }
        facts = list(
            csv.DictReader(io.StringIO(archive.read("financials.csv").decode("utf-8-sig")))
        )
        assert len(facts) == 24
        assert {r["fact_id"] for r in facts} == set(dataset.selected_ids)
        assert any(Decimal(r["value"]) == -24 for r in facts)
    workbook = load_workbook(io.BytesIO(excel_bytes(dataset, calculations)))
    assert workbook.sheetnames == ["financials", "calculations", "sources", "warnings", "metadata"]
    assert all(c.data_type != "f" for sheet in workbook for row in sheet for c in row)


def test_spreadsheet_injection_escaped():
    data = import_csv(alter(source_reference='=HYPERLINK("https://evil.invalid")'))
    # Source references are embedded in a safe upload identifier; company fields also escaped.
    from finsight.exports import csv_bytes

    text = csv_bytes([{"company": " =1+1", "negative_amount": Decimal("-2")}]).decode("utf-8-sig")
    row = list(csv.DictReader(io.StringIO(text)))[0]
    assert row["company"].startswith("'") and row["negative_amount"] == "-2"
    workbook = load_workbook(io.BytesIO(excel_bytes(data, calculate(data))))
    assert all(c.data_type != "f" for sheet in workbook for row in sheet for c in row)
