"""Select recent disclosure evidence without normalizing mixed reporting periods."""

import re
from datetime import date


def valid_date(value):
    """Strict ISO calendar dates only; labels and malformed dates cannot rank latest."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def excerpt(document, patterns, limit=2):
    candidates = []
    for passage in document.passages:
        if not 80 <= len(passage.text) <= 3000:
            continue
        score = sum(bool(re.search(pattern, passage.text, re.I)) for pattern in patterns)
        if score and sum(c.isdigit() for c in passage.text) / len(passage.text) < 0.15:
            candidates.append((score, passage))
    return [p for _, p in sorted(candidates, key=lambda item: -item[0])[:limit]]


def period_basis(text):
    labels = []
    if re.search(
        r"three(?: and (?:six|nine))? months|3 months|\bquarter\b|quarterly (?:revenue|results|income|sales|earnings)|\b(?:Q[1-4]|[1-4]Q)\b",
        text,
        re.I,
    ):
        labels.append("quarterly (three months)")
    if re.search(
        r"six months|nine months|[69] months|half.year|first half|\b1H\b|year.to.date", text, re.I
    ):
        labels.append("year-to-date / half-year (six or nine months; inspect source)")
    if re.search(r"twelve months|year ended|annual results|full.year", text, re.I):
        labels.append("annual")
    return "; ".join(labels) or "duration not established from this excerpt"


def is_interim(document):
    header = " ".join(p.text for p in document.passages[:40])
    return document.title.startswith(("10-Q ", "10-Q/A ")) or (
        document.kind == "earnings/event exhibit"
        and bool(re.search(r"interim condensed consolidated.{0,40}financial", header, re.I))
    )


def recent_evidence(documents):
    """Latest registered interim, plus latest readable results exhibit (not arbitrary ex99)."""
    groups = []
    supplementary = []

    def dated(candidates):
        eligible = []
        for doc in candidates:
            published = valid_date(doc.published)
            if published is None:
                reason = (
                    "Publication date unavailable"
                    if doc.published in {"", "Not established", "Not specified"}
                    else "Invalid publication date"
                )
                supplementary.append(
                    (f"Supplementary evidence — {reason}; excluded from latest ranking", doc)
                )
            else:
                eligible.append(doc)
        return eligible

    interims = dated([d for d in documents if is_interim(d)])
    if interims:
        groups.append(
            (
                "Latest interim filing",
                max(
                    interims,
                    key=lambda d: (valid_date(d.period) or date.min, valid_date(d.published)),
                ),
            )
        )
    earnings = [
        d
        for d in documents
        if d.kind in {"earnings/event exhibit", "IR linked document", "current report"}
        and d.status == "read"
        and not is_interim(d)
        and any(
            re.search(
                r"(?:quarter|half.year|annual|financial).{0,40}results|results.{0,40}(?:quarter|year)|earnings release",
                p.text,
                re.I,
            )
            for p in d.passages[:100]
        )
    ]
    earnings = dated(earnings)
    if earnings:
        groups.append(
            (
                "Latest accessible earnings/results disclosure",
                max(
                    earnings,
                    key=lambda d: (valid_date(d.published), d.kind == "earnings/event exhibit"),
                ),
            )
        )
    output = []
    for label, doc in groups + supplementary:
        passages = (
            excerpt(
                doc,
                [
                    r"(?:revenue|sales|income|cash).{0,180}(?:increased|decreased|growth|decline)",
                    r"(?:due to|driven by|primarily|reflect).{0,100}(?:revenue|sales|cost|demand)",
                    r"(?:quarter|months|year).{0,50}ended",
                    r"financial results|guidance|outlook",
                ],
                3,
            )
            if doc.status == "read"
            else []
        )
        passages = [
            p
            for p in passages
            if not re.search(r"conference call|webcast|live streaming", p.text, re.I)
        ]
        # Preserve source period headings even when separate from a selected narrative paragraph.
        context = [
            p
            for p in doc.passages[:500]
            if re.search(
                r"(?:three|six|nine|twelve|3|6|9|12) months ended|(?:quarter|year) ended|half.year|year.to.date",
                p.text,
                re.I,
            )
        ][:2]
        selected = list(dict.fromkeys(context + passages)) if doc.status == "read" else []
        warnings = []
        if valid_date(doc.period) is None:
            warnings.append(
                "Report-period date unavailable or invalid; no reporting period inferred."
            )
        if valid_date(doc.published) is None:
            warnings.append(
                "Publication date unavailable or invalid; supplementary only, not latest evidence."
            )
        output.append(
            {
                "label": label,
                "document": doc,
                "passages": selected,
                "latest_eligible": valid_date(doc.published) is not None,
                "date_warnings": warnings,
            }
        )
    return output
