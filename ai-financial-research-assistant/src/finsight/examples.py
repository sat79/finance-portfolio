"""Explicitly fictional example, never used as an automatic SEC fallback."""

from pathlib import Path

from finsight.csv_import import import_csv
from finsight.models import Dataset


def synthetic_example(path: Path) -> Dataset:
    original = import_csv(path.read_bytes())
    facts = tuple(f.model_copy(update={"status": "synthetic"}) for f in original.observations)
    return Dataset(
        company=original.company,
        cik=original.cik,
        origin="synthetic_fixture",
        fetched_at=original.fetched_at,
        periods=original.periods,
        observations=facts,
        selected_ids=tuple(f.id for f in facts),
        warnings=original.warnings,
        policy="Fictional fixed teaching dataset, FY2022–FY2024; not live or historical SEC evidence.",
        source_hashes=original.source_hashes,
    )
