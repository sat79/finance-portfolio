"""Select recent disclosure evidence without normalizing mixed reporting periods."""

import re
from datetime import date

from finsight.research.selection import select_passages


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
    unique_supplements, supplement_signatures, duplicate_documents = [], {}, {}
    for label, doc in supplementary:
        records = select_passages(doc, supplementary=True)
        signature = tuple(
            doc.passages[i].text for r in records for i in [*r["context_indices"], r["index"]]
        )
        if signature and signature in supplement_signatures:
            duplicate_documents.setdefault(supplement_signatures[signature], []).append(doc.id)
        else:
            if signature:
                supplement_signatures[signature] = doc.id
            unique_supplements.append((label, doc))
    # At most two undated supplements; no undated record displaces dated evidence.
    for label, doc in groups + unique_supplements[:2]:
        records = select_passages(doc, supplementary=valid_date(doc.published) is None)
        indices = list(
            dict.fromkeys(i for r in records for i in [*r["context_indices"], r["index"]])
        )
        selected = [doc.passages[i] for i in indices]
        # Small unquantified disclosures can still supply exact period context, without a forced finding.
        if not selected and doc.status == "read":
            selected = [
                p
                for p in excerpt(doc, [r"financial results|quarter|months ended"], 1)
                if len(p.text) <= 1600
            ]
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
                "records": records,
                "duplicate_document_ids": duplicate_documents.get(doc.id, []),
                "selection_limit": "Six primary passages per dated document, three context passages per primary; at most two single-passage undated supplements.",
                "latest_eligible": valid_date(doc.published) is not None,
                "date_warnings": warnings,
            }
        )
    return output
