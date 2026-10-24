"""Bounded topic selection; source context is retained, never normalized into new facts."""

import re

MAX_PRIMARY = 6
MAX_CONTEXT = 3
MAX_PASSAGE_CHARS = 1600
TOPICS = ("results", "credit_risk", "drivers", "explanation", "capital")
PERIOD = r"\b(?:[1-4]Q|Q[1-4]|[1-4]H|H[1-4])\s*20\d\d\b|(?:three|six|nine|twelve|3|6|9|12) months ended|(?:quarter|year) ended|(?:first|second|third|fourth) quarter|half.year"
BOILERPLATE = r"conference call|webcast|forward.looking statements|same accounting policies|methods of computation|table of contents|press contact"
CAUSE = r"due to|driven by|growth driver|primarily|supported by|reflect(?:s|ing)?|because|even with|as a result|resulting in|impacted"


def matches(pattern, text):
    return bool(re.search(pattern, text, re.I))


def scores(text):
    if not 40 <= len(text) <= MAX_PASSAGE_CHARS or matches(BOILERPLATE, text):
        return {}
    if not re.search(r"\d", text) or len(re.findall(r"[A-Za-z]{2,}", text)) < 6:
        return {}
    result = {}
    amount = matches(
        r"(?:[$€£₸]|KZT|USD)\s*[\d,]+|\d[\d,.]*\s*(?:%|percent|bps|billion|million)", text
    )
    movement = matches(
        r"was|were|grew|increas|decreas|rose|declin|amounted|stable|totaled|up |down |reached", text
    )
    metrics = len(
        re.findall(
            r"revenue|net sales|net income|net profit|earnings per share|\bEPS\b|operating income|EBITDA",
            text,
            re.I,
        )
    )
    if (
        amount
        and movement
        and matches(
            r"net income|net profit|diluted|earnings per share|\bEPS\b|total (?:revenue|net sales)|^(?:revenue|operating income)|(?:company|group|consolidated).{0,60}(?:revenue|sales)",
            text,
        )
    ):
        result["results"] = (
            5
            + min(metrics, 4) * 2
            + 8 * matches(r"revenue|net sales", text)
            + 6 * matches(r"net income|net profit", text)
        )
        if matches(
            r"impact from investments|following table|acquired|consideration|discrete items", text
        ):
            result["results"] -= 12
        if matches(r"segment|parent|attributable|non.controlling", text):
            result["results"] -= 3
    if matches(
        r"stage [123]|non.performing|restructured loans|credit losses|loan.loss|capital adequacy|liquidity coverage",
        text,
    ):
        result["credit_risk"] = (
            7
            + 4 * matches(r"stage 3|restructured|non.performing", text)
            + 3 * matches(r"as at|as of|respectively", text)
            + 3 * matches(r"gross carrying", text)
        )
    if (
        amount
        and not matches(r"repurchase|commercial paper|acquired|following table|cost of goods", text)
        and matches(
            r"growth driver|GMV|TPV|take.rate|purchases|cloud|azure|subscriptions|services|devices|volume|advertising|delivery|product mix",
            text,
        )
        and matches(r"growth|increas|decreas|grew|declin|up |down |rate|outpaced", text)
    ):
        result["drivers"] = (
            5
            + 5 * matches(r"take.rate|outpaced", text)
            + 10 * matches(r"growth driver", text)
            + 2 * matches(r"constant.currency", text)
            + 3 * matches(r"(?:[$€£₸]|KZT|USD)\s*[\d,.]+\s*(?:billion|million|trillion)", text)
            + len(re.findall(r"GMV|TPV|purchases|take.rate|revenue|cloud|services", text, re.I))
        )
    if (
        matches(CAUSE, text)
        and matches(
            r"increas|decreas|grew|declin|growth|higher|lower|impacted|benefit|reduced|stable", text
        )
        and matches(r"revenue|sales|income|profit|cost|expense|margin|cash|funding", text)
    ):
        result["explanation"] = 5 + 4 * matches(
            r"funding costs|interest expense|product mix|tariff|discrete|one.time", text
        )
        if matches(r"intergroup|placement of cash|we may|could", text):
            result["explanation"] -= 5
    if matches(
        r"dividend|repurchase|buyback|acquisition of|acquired|interest rate.{0,50}deposit|deposit.{0,50}rate",
        text,
    ):
        result["capital"] = 5 + 2 * matches(r"approved|declared|proposed|completed|reduced", text)
    return result


def similar(a, b):
    left, right = (set(re.findall(r"\w+", t.casefold())) for t in (a, b))
    if left and right and len(left & right) / len(left | right) >= 0.78:
        return True

    # Repeated highlights and segment discussion often repeat the same measures in different prose.
    def numbers(text):
        return {
            n
            for n in re.findall(r"\d+(?:[.,]\d+)*", text)
            if not re.fullmatch(r"(?:19|20)\d{2}", n) and (len(n) > 1 or "." in n)
        }

    na, nb = numbers(a), numbers(b)
    measures = r"revenue|net income|GMV|TPV|take.rate|purchases|margin"
    ma, mb = (set(re.findall(measures, t.casefold(), re.I)) for t in (a, b))
    return bool(
        min(len(na), len(nb)) >= 4
        and len(na & nb) / min(len(na), len(nb)) >= 0.8
        and len(ma & mb) >= 2
    )


def nearby_context(document, index):
    """Nearest explicit period/section/unit text, plus dated reporting overview if space allows."""
    passages = document.passages
    selected = []
    preceding = list(range(max(0, index - 60), index))
    found = next(
        (
            j
            for j in reversed(preceding)
            if len(passages[j].text) < 160
            and matches(PERIOD, passages[j].text)
            and matches(r"20\d\d", passages[j].text)
            and not matches(
                r"increased|decreased|proposed|revenue|dividend|collected|amounted|KZT|USD|[$€£₸]",
                passages[j].text,
            )
        ),
        None,
    )
    if found is not None:
        selected.append(found)
    if not matches(r"million|billion|trillion|KZT|USD|[$€£₸]", passages[index].text):
        found = next(
            (
                j
                for j in reversed(preceding[-12:])
                if len(passages[j].text) < 180
                and matches(
                    r"in (?:millions|thousands)|except per.share|expressed in", passages[j].text
                )
            ),
            None,
        )
        if found is not None:
            selected.append(found)
    heading = passages[index].heading
    found = next(
        (
            j
            for j in reversed(preceding)
            if (heading and passages[j].text == heading)
            or (
                len(passages[j].text) < 100
                and matches(
                    r"^(?:[\d. ]+)?(?:credit risk|capital adequacy|fintech|payments|marketplace|intelligent cloud|productivity and business|more personal computing|segment results|consolidated results)$",
                    passages[j].text,
                )
            )
        ),
        None,
    )
    if found is not None:
        selected.append(found)
    # A release introduction may establish the reporting end date beyond the local heading.
    overview = next(
        (
            j
            for j, p in enumerate(passages[:12])
            if j < index
            and len(p.text) <= 700
            and matches(r"(?:quarter|half|months).{0,60}ended", p.text)
            and matches(r"20\d\d", p.text)
            and matches(
                r"results|financial statements|financial information|announced|published", p.text
            )
        ),
        None,
    )
    if overview is not None:
        selected.append(overview)
    return list(dict.fromkeys(selected))[:MAX_CONTEXT]


def select_passages(document, *, supplementary=False):
    if document.status != "read":
        return []
    ranked = [(i, scores(p.text)) for i, p in enumerate(document.passages)]
    selected = []
    # Two operating-driver slots capture volume and monetization without letting generic results dominate.
    slots = ["results", "credit_risk", "drivers", "explanation", "drivers", "capital"]
    for topic in slots[:1] if supplementary else slots:
        candidates = sorted(
            ((s[topic], i) for i, s in ranked if topic in s), key=lambda x: (-x[0], x[1])
        )
        for score, index in candidates:
            text = document.passages[index].text
            if any(similar(text, document.passages[r["index"]].text) for r in selected):
                continue
            selected.append(
                {
                    "index": index,
                    "topic": topic,
                    "score": score,
                    "context_indices": nearby_context(document, index),
                }
            )
            break
    # Short split earnings bullets (e.g. revenue and net income) need a second result if another slot is unused.
    if len(selected) < (1 if supplementary else MAX_PRIMARY) and not any(
        r["topic"] == "results"
        and matches(
            r"net income|net profit|earnings per share|diluted", document.passages[r["index"]].text
        )
        for r in selected
    ):
        for _, index in sorted(
            ((s["results"], i) for i, s in ranked if "results" in s), key=lambda x: (-x[0], x[1])
        ):
            if not matches(
                r"net income|net profit|earnings per share", document.passages[index].text
            ):
                continue
            if any(
                similar(document.passages[index].text, document.passages[r["index"]].text)
                for r in selected
            ):
                continue
            selected.append(
                {
                    "index": index,
                    "topic": "results",
                    "score": scores(document.passages[index].text)["results"],
                    "context_indices": nearby_context(document, index),
                }
            )
            if len(selected) >= (1 if supplementary else MAX_PRIMARY):
                break
    return selected
