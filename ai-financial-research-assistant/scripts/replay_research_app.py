"""Browser test harness for saved research snapshots; never used by the production app.

FINSIGHT_REPLAY_DIR must contain the four *-evidence.json validation snapshots.
Run with Streamlit from the project directory. All external calls are replaced.
"""

import json
import os
import runpy
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import streamlit as st

from finsight.models import Dataset
from finsight.research.models import Company, Document, NewsItem, Passage, Research

root = Path(__file__).resolve().parents[1]
folder = Path(os.environ["FINSIGHT_REPLAY_DIR"])
results = {}
for ticker in ["AAPL", "MSFT", "KSPI", "NVDA"]:
    raw = json.loads((folder / f"{ticker}-evidence.json").read_text())
    raw["company"] = Company(**raw["company"])
    raw["cutoff"] = datetime.fromisoformat(raw["cutoff"])
    for field in ["news_start", "news_end"]:
        raw[field] = date.fromisoformat(raw[field])
    raw["documents"] = [
        Document(**{**d, "passages": [Passage(**p) for p in d["passages"]]})
        for d in raw["documents"]
    ]
    raw["news"] = [NewsItem(**n) for n in raw["news"]]
    raw["dataset"] = Dataset.model_validate(raw["dataset"]) if raw["dataset"] else None
    raw["limitations"].insert(
        0,
        "TEST REPLAY: dated saved evidence; no fresh network requests. Directory matches are test fixtures.",
    )
    results[ticker] = Research(**raw)


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
