"""Evidence-first key findings: quoted statements, existing calculations and open questions."""

import re

from finsight.financials import calculate
from finsight.research.evidence import is_interim, recent_evidence
from finsight.research.selection import CAUSE, similar

QUESTIONS = {
    "results": "What explains the reported movement after separating reporting scope, currency and one-off items? The selected evidence does not quantify a causal bridge.",
    "drivers": "How do the named operating measures translate into comparable revenue and profit? Keep segment measures, volumes and reported/constant-currency growth separate.",
    "credit_risk": "What are the exposure denominator, coverage and movements behind this disclosed risk measure? A loan subset is not total NPLs or a loss rate; balance-sheet dates are not quarterly flows.",
    "explanation": "Does other evidence corroborate this management explanation, and how much of the movement does it explain? No causal contribution is calculated here.",
    "capital": "What cash, funding, approvals and restrictions support this action? A proposal or approval is not proof of payment or sustainable distributions.",
}
TITLES = {
    "results": "Latest reported results",
    "drivers": "Operating drivers",
    "credit_risk": "Credit-risk evidence",
    "explanation": "Management's explanation",
    "capital": "Capital and distributions",
}


def key_findings(research, selections=None):
    selections = selections if selections is not None else recent_evidence(research.documents)
    candidates = []
    for selection in selections:
        if not selection["latest_eligible"]:
            continue
        doc = selection["document"]
        for record in selection["records"]:
            passage = doc.passages[record["index"]]
            if len(passage.text) > 900:
                continue  # Do not cut off qualifying language to fit a finding.
            candidates.append((doc, record))
    output, used = [], []

    def source_finding(topic):
        options = [
            (d, r)
            for d, r in candidates
            if r["topic"] == topic
            and not any(similar(d.passages[r["index"]].text, t) for t in used)
        ]
        # Prefer the latest results release for results/drivers, not an undated or older supplement.
        options.sort(
            key=lambda dr: (
                not is_interim(dr[0]),
                dr[1]["score"],
                dr[0].published,
            ),
            reverse=True,
        )
        if not options:
            return
        doc, record = options[0]
        chosen = [(doc, record)]
        if topic in {"results", "drivers"}:
            for other_doc, other in options[1:]:
                if other_doc.id != doc.id:
                    continue
                texts = [d.passages[r["index"]].text for d, r in chosen]
                candidate = other_doc.passages[other["index"]].text
                if sum(map(len, texts)) + len(candidate) <= 1200 and not any(
                    similar(candidate, t) for t in texts
                ):
                    chosen.append((other_doc, other))
                    break
        statements, context = [], []
        for doc, record in chosen:
            text = doc.passages[record["index"]].text
            key = f"{doc.id}:B{record['index'] + 1}"
            sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z“])", text)
            statements.extend(
                {
                    "kind": "management explanation"
                    if re.search(CAUSE, s, re.I)
                    else "reported fact",
                    "text": s,
                    "citation_id": key,
                }
                for s in sentences
            )
            context.extend(f"{doc.id}:B{i + 1}" for i in record["context_indices"])
            used.append(text)
        output.append(
            {
                "title": TITLES[topic],
                "topic": topic,
                "statements": statements,
                "context_citation_ids": list(dict.fromkeys(context)),
                "calculation_ids": [],
                "question": QUESTIONS[topic],
                "boundary": "Source statements are not independently verified. Preserve the quoted period, units and named entity/measure; no annualization or scope substitution.",
            }
        )

    source_finding("results")
    if research.dataset and research.dataset.selected:
        calculations = calculate(research.dataset)
        ends = sorted({c.period_end for c in calculations})
        keep = [
            (i, c)
            for i, c in enumerate(calculations, 1)
            if c.value is not None
            and (
                (c.metric == "revenue_growth" and c.period_end == ends[-1])
                or (c.metric == "net_margin" and c.period_end in ends[-2:])
            )
        ]
        if keep:
            output.append(
                {
                    "title": "Annual reported growth and profitability",
                    "topic": "annual_calculations",
                    "statements": [],
                    "context_citation_ids": [],
                    "calculation_ids": [f"C{i}" for i, _ in keep],
                    "question": "Are the annual observations comparable in business scope and accounting basis? These calculations do not establish organic growth or explain a newer quarter.",
                    "boundary": "Annual group net-income margin is not parent-attributable profit or operating margin. Reported growth is not constant-currency growth. See all input warnings.",
                }
            )
    for topic in ["drivers", "credit_risk", "explanation", "capital"]:
        if len(output) >= 5:
            break
        source_finding(topic)
    return output
