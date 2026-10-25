"""Bounded HTML cell evidence. No reconstruction from flattened prose or numeric normalization."""

import json
import re
from html.parser import HTMLParser

MAX_TABLES = 4
MAX_ROWS = 12
MAX_COLUMNS = 40
MAX_EVIDENCE_BYTES = 96 * 1024
NUMBER = re.compile(r"^[($€£−–-]*\s*\d[\d,.]*\s*[)%]*$|^[—–-]$")
MONTH = r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
MONTH_WORD = r"\b(?:" + MONTH + r")\b"
SCOPE = r"months? ended|years? ended|quarter|year.to.date|as (?:at|of)|balance sheets"
OPERATING_CASH = r"cash.*(?:operating|from operations|(?:provided by|used in) operations)"
METRIC = rf"revenue|net sales|net income|net profit|operating income|{OPERATING_CASH}|total assets|total liabilities|credit losses|restructured loans"


def match(pattern, text):
    return bool(re.search(pattern, text, re.I))


class TableHTML(HTMLParser):
    """Record original table/row/cell ordinals and tag positions before applying rowspan/colspan."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.stack, self.context = [], [], []
        self.buffer, self.start = [], None
        self.ignored = 0
        self.count = 0

    def flush_context(self):
        text = " ".join("".join(self.buffer).split())
        if text and len(text) <= 500:
            self.context.append({"text": text, "position": self.start})
            self.context = self.context[-8:]
        self.buffer, self.start = [], None

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "head", "ix:hidden"}:
            self.ignored += 1
        if self.ignored:
            return
        if tag == "table":
            self.flush_context()
            self.count += 1
            table = {
                "ordinal": self.count,
                "position": list(self.getpos()),
                "context": list(self.context),
                "rows": [],
                "errors": [],
            }
            if self.stack:
                self.stack[-1]["errors"].append("Nested table; parent alignment unsupported.")
                table["errors"].append("Nested table; inherited context unsupported.")
            self.stack.append(table)
            if self.count <= 200:
                self.tables.append(table)
            return
        if self.stack:
            table = self.stack[-1]
            if tag == "tr":
                if table.get("cell") is not None:
                    table["errors"].append("Unclosed cell before next row; structure ambiguous.")
                    table.pop("cell", None)
                if len(table["rows"]) >= 500:
                    table["errors"].append("Table exceeds 500-row parse limit.")
                    table["cell"] = None
                    return
                table["rows"].append([])
            if tag in {"td", "th"} and table["rows"] and len(table["rows"]) < 500:
                if table.get("cell") is not None:
                    table["errors"].append("Unclosed cell before next cell; structure ambiguous.")
                row = table["rows"][-1]
                attrs = dict(attrs)
                cell = {
                    "row": len(table["rows"]),
                    "cell": len(row) + 1,
                    "position": list(self.getpos()),
                    "text": "",
                    "tag": tag,
                }
                for key in ["rowspan", "colspan"]:
                    value = attrs.get(key, "1")
                    if not value.isdigit() or not 1 <= int(value) <= MAX_COLUMNS:
                        table["errors"].append("Invalid or oversized cell span.")
                        value = "1"
                    cell[key] = int(value)
                row.append(cell)
                table["cell"] = cell
            if tag in {"br", "p", "div"} and table.get("cell") is not None:
                table["cell"]["text"] += " "
        elif tag in {"p", "div", "h1", "h2", "h3", "br"}:
            self.flush_context()

    def handle_data(self, data):
        if self.ignored:
            return
        if self.stack:
            cell = self.stack[-1].get("cell")
            if cell is not None:
                if len(cell["text"]) + len(data) > 800:
                    self.stack[-1]["errors"].append("Cell exceeds 800-character limit.")
                cell["text"] = (cell["text"] + data)[:801]
        else:
            if self.start is None:
                self.start = list(self.getpos())
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag in {"script", "style", "head", "ix:hidden"} and self.ignored:
            self.ignored -= 1
            return
        if self.ignored:
            return
        if tag == "table" and self.stack:
            self.stack.pop().pop("cell", None)
            if not self.stack:
                self.context = []
        elif tag in {"td", "th"} and self.stack:
            cell = self.stack[-1].pop("cell", None)
            if cell:
                cell["text"] = " ".join(cell["text"].split())
        elif tag in {"p", "div", "h1", "h2", "h3"} and not self.stack:
            self.flush_context()


def place_cells(table):
    occupied = set()
    for row_index, row in enumerate(table["rows"]):
        column = 0
        for cell in row:
            while (row_index, column) in occupied:
                column += 1
            cell["column"] = column + 1
            if row_index + cell["rowspan"] > len(table["rows"]):
                raise ValueError("Row span extends beyond table; structure incomplete.")
            if column + cell["colspan"] > MAX_COLUMNS:
                raise ValueError("Table exceeds 40 physical columns.")
            for r in range(row_index, row_index + cell["rowspan"]):
                for c in range(column, column + cell["colspan"]):
                    if (r, c) in occupied:
                        raise ValueError("Overlapping cell spans; alignment ambiguous.")
                    occupied.add((r, c))
            column += cell["colspan"]


def data_cells(row):
    nonempty = [c for c in row if c["text"]]
    if not nonempty or not re.search(r"[A-Za-z]", nonempty[0]["text"]):
        return None, []
    label = nonempty[0]
    if match(
        r"^(?:three|six|nine|twelve|years? ended|quarters? ended|as of|as at|\(?in millions|\(?unaudited)\b",
        label["text"],
    ) or match(r"^(?:" + MONTH + r")\b", label["text"]):
        return None, []
    values = [c for c in nonempty[1:] if NUMBER.fullmatch(c["text"])]
    return label, values


def selected_table(table):
    context = table["context"]
    titles = [
        i
        for i, c in enumerate(context)
        if match(r"statements? of|balance sheets|income statements?", c["text"])
    ]
    context = context[max(0, titles[-1] - 1) :] if titles else context[-3:]
    candidates, section = [], None
    first_data = None
    for row in table["rows"]:
        label, values = data_cells(row)
        if label and values:
            if first_data is None:
                first_data = label["row"]
            text = label["text"]
            score = 10 if match(METRIC, text) else 0
            if section and match(
                r"net sales|revenue|reportable segment|by category", section["text"]
            ):
                score = max(score, 5)
            if score:
                candidates.append((score, row, label, values, section))
        elif label and not values and len(label["text"]) <= 160:
            section = label
    if not candidates:
        text = " ".join(c["text"] for row in table["rows"] for c in row)
        if re.search(r"\d[\d,]+", text) and match(
            r"reconciliation|statements|revenue|financial", " ".join(c["text"] for c in context)
        ):
            return {
                "table": table["ordinal"],
                "position": table["position"],
                "context": context,
                "status": "unsupported",
                "notes": [
                    "No supported metric-row layout; column-oriented or fragmented measures are not transposed by guessing."
                ],
                "rows": [],
            }
        return None
    result = {
        "table": table["ordinal"],
        "position": table["position"],
        "context": context,
        "status": "unsupported",
        "notes": list(dict.fromkeys(table["errors"])),
        "rows": [],
    }
    if result["notes"]:
        return result
    try:
        place_cells(table)
    except ValueError as exc:
        result["notes"].append(str(exc))
        return result
    headers = [
        c
        for row in table["rows"][: first_data - 1]
        for c in row
        if c["text"]
        and (c["column"] > 1 or match(SCOPE + "|" + MONTH_WORD + r"|\b20\d{2}\b", c["text"]))
    ]
    if first_data > 13:
        result["notes"].append("More than 12 header rows; unsupported header layout.")
        return result
    result["headers"] = headers
    units = [
        c
        for c in [*context, *headers]
        if match(r"in (?:millions|thousands)|KZT.*million|USD.*million", c["text"])
    ]
    result["units"] = units
    if not units:
        result["notes"].append("Explicit table scale/unit heading missing; amounts not mapped.")
        return result
    for _, row, label, values, section in sorted(candidates, key=lambda x: (-x[0], x[2]["row"]))[
        :MAX_ROWS
    ]:
        mapped, reason = [], ""
        for value in values:
            left, right = value["column"], value["column"] + value["colspan"]
            path = [
                h for h in headers if h["column"] <= left and h["column"] + h["colspan"] >= right
            ]
            text = " ".join(h["text"] for h in path)
            # A shared outside-table duration may qualify dates, never supply missing dates.
            scope = " ".join(c["text"] for c in context) + " " + text
            if not (
                match(MONTH_WORD, text) and match(r"\b20\d{2}\b", text) and match(SCOPE, scope)
            ):
                reason = "Column date/year or reporting-duration/instant heading unresolved."
                break
            mapped.append({"value_cell": value, "column_headers": path})
        if len(values) > 8:
            reason = "Row exceeds eight value-cell budget."
        if len({tuple(h["text"].casefold() for h in m["column_headers"]) for m in mapped}) != len(
            mapped
        ):
            reason = "Multiple value cells share indistinguishable column headings."
        result["rows"].append(
            {
                "row": label["row"],
                "label": label["text"],
                "section": section,
                "source_cells": row,
                "values": mapped if not reason else [],
                "status": "structured" if not reason else "ambiguous",
                "reason": reason,
            }
        )
    result["rows"].sort(key=lambda r: r["row"])
    result["omitted_candidate_rows"] = max(0, len(candidates) - MAX_ROWS)
    result["omitted_row_labels"] = [
        x[2]["text"]
        for x in sorted(candidates, key=lambda x: (-x[0], x[2]["row"]))[MAX_ROWS : MAX_ROWS + 12]
    ]
    result["status"] = (
        "structured" if all(r["status"] == "structured" for r in result["rows"]) else "partial"
    )
    result["notes"].append(
        "Source cell text and spans only; no currency-code inference, arithmetic, annual substitution or normalized observations. Blank and currency/sign cells remain in source_cells."
    )
    return result


def table_priority(table):
    """Rank explicit financial headings before budgets; never infer a cell's accounting scope."""
    title = " ".join(c["text"] for c in table["context"])
    labels = " ".join(r["label"] for r in table["rows"])
    if match(r"segment.*(?:revenue|income)|(?:revenue|income).*segment", title):
        rank = 0
    elif match(r"cash flows?|cash.*operations", title) or match(OPERATING_CASH, labels):
        rank = 1
    elif match(r"comprehensive", title):
        rank = 4
    elif match(r"income statements?|statements? of (?:income|operations)|financial results", title):
        rank = 2
    elif match(r"balance sheets|financial position", title):
        rank = 3
    else:
        rank = 5
    # A wholly ambiguous table cannot displace a table with supported rows.
    return (not any(r["status"] == "structured" for r in table["rows"]), rank, table["table"])


def extract_tables(content, media):
    if content.startswith(b"%PDF") or "html" not in media:
        return [], [
            "Structural table extraction unsupported for this format; flattened numbers are not mapped."
        ]
    parser = TableHTML()
    parser.feed(content.decode("utf-8", errors="replace"))
    if parser.stack:
        for t in parser.stack:
            t["errors"].append("Unclosed table; structure incomplete.")
    tables = [t for raw in parser.tables if (t := selected_table(raw)) is not None]
    unsupported = [t for t in tables if t["status"] == "unsupported"]
    tables = sorted([t for t in tables if t["status"] != "unsupported"], key=table_priority)
    notes = [
        f"Selected at most {MAX_TABLES} financial tables, {MAX_ROWS} rows per table and eight values per row; header limit 12 rows. {max(0, len(tables) - MAX_TABLES)} additional candidate tables omitted."
    ]
    notes.append(
        "Candidate tables ranked by supported rows and explicit financial/segment headings before existing budgets; original table and row ordinals preserved."
    )
    if len(tables) > MAX_TABLES:
        notes.append(
            "Table-count budget omitted candidate ordinals: "
            + ", ".join(str(t["table"]) for t in tables[MAX_TABLES:])
        )
    if parser.count > 200:
        notes.append("Only the first 200 HTML tables were inspected.")
    notes.extend(f"Table {t['table']} unsupported: {' '.join(t['notes'])}" for t in unsupported[:8])
    if len(unsupported) > 8:
        notes.append(
            f"{len(unsupported) - 8} additional unsupported tables omitted from diagnostics."
        )
    bounded, size = [], 0
    for table in tables[:MAX_TABLES]:
        amount = len(json.dumps(table).encode())
        if size + amount > MAX_EVIDENCE_BYTES:
            notes.append(
                f"Table {table['table']} omitted: 96 KiB structural evidence budget exceeded."
            )
            continue
        bounded.append(table)
        size += amount
    # Retain a bounded diagnostic record when no mappable tables exist.
    fallback = [
        {k: t[k] for k in ["table", "position", "context", "status", "notes", "rows"]}
        for t in unsupported[:1]
    ]
    return bounded or fallback, notes
