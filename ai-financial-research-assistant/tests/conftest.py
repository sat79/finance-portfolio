import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from finsight.selection import select_annual

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def raw():
    return json.loads((ROOT / "tests/fixtures/synthetic_companyfacts.json").read_text())


@pytest.fixture
def submissions():
    return json.loads((ROOT / "tests/fixtures/synthetic_submissions.json").read_text())


@pytest.fixture
def dataset(raw, submissions):
    return select_annual(
        raw,
        submissions,
        cik="0000000001",
        origin="synthetic_fixture",
        fetched_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
