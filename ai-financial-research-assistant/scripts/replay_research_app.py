"""Browser test harness for saved research snapshots; never used by the production app.

FINSIGHT_REPLAY_DIR must contain the four *-evidence.json validation snapshots.
Run with Streamlit from the project directory. All external calls are replaced.
"""

import json
import os
import runpy
from pathlib import Path
from unittest.mock import patch

import streamlit as st

from finsight.research.models import Company, from_snapshot
from finsight.research.news import enrich_news
from finsight.sec import SECError

root = Path(__file__).resolve().parents[1]
folder = Path(os.environ["FINSIGHT_REPLAY_DIR"])
results = {}
for ticker in ["AAPL", "MSFT", "KSPI", "NVDA"]:
    raw = json.loads((folder / f"{ticker}-evidence.json").read_text())
    result = from_snapshot(raw)
    result.limitations.insert(
        0,
        "TEST REPLAY: dated saved evidence; no fresh network requests. Directory matches are test fixtures.",
    )

    class ReplayOnly:
        def get(self, *args, **kwargs):
            raise SECError("Replay only: original source not in snapshot; no request made.")

    enrich_news(ReplayOnly(), result.news, result.documents)
    results[ticker] = result


def find(_client, query):
    matches = [
        r.company
        for r in results.values()
        if query.lower() in r.company.name.lower() or query.upper() == r.company.ticker
    ]
    if query.lower() == "apple":
        matches.append(Company("Apple Hospitality REIT", "APLE", "NYSE", "0001715948"))
    return matches


def research(company, *args, **kwargs):
    return results[company.ticker]


st.warning("TEST REPLAY ONLY — historical snapshots, not current live validation")
with (
    patch("finsight.research.ui.SECClient"),
    patch("finsight.research.ui.find_companies", find),
    patch("finsight.research.ui.run_research", research),
):
    runpy.run_path(str(root / "app/main.py"), run_name="__main__")
