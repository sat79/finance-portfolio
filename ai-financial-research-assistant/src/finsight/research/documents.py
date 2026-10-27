"""Readable HTML/PDF evidence with real text-block or PDF-page locations; no OCR claims."""

import io
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from finsight.research.models import Document, Passage
from finsight.research.publisher import guardian_article
from finsight.research.tables import extract_tables
from finsight.research.transport import EvidenceClient
from finsight.sec import SECError


class FilingHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.links = []
        self.buffer = []
        self.heading = ""
        self.heading_tag = False
        self.ignored = 0

    def flush(self):
        text = " ".join("".join(self.buffer).split())
        self.buffer = []
        if text:
            if self.heading_tag:
                self.heading = text[:200]
            for start in range(0, len(text), 3000):
                self.blocks.append(
                    Passage(
                        f"HTML text block {len(self.blocks) + 1}",
                        text[start : start + 3000],
                        self.heading,
                    )
                )

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "head", "ix:hidden"}:
            self.ignored += 1
        if self.ignored:
            return
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href:
                self.links.append(href)
        if tag in {"p", "div", "tr", "br", "li", "h1", "h2", "h3", "h4"}:
            self.flush()
            self.heading_tag = tag in {"h1", "h2", "h3", "h4"}
        if tag in {"td", "th"}:
            self.buffer.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "head", "ix:hidden"} and self.ignored:
            self.ignored -= 1
            return
        if not self.ignored and tag in {"p", "div", "tr", "li", "h1", "h2", "h3", "h4"}:
            self.flush()
            self.heading_tag = False

    def handle_data(self, data):
        if not self.ignored:
            self.buffer.append(data)


class GuardianArticleHTML(FilingHTML):
    """Read only the publisher's marked public article body, excluding site navigation."""

    def __init__(self):
        super().__init__()
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        marked = (
            attributes.get("data-gu-name") == "body"
            or attributes.get("data-test-id") == "article-body"
            or "article-body-viewer-selector" in classes
            or "content__article-body" in classes
        )
        if not self.depth and tag == "div" and marked:
            self.depth = 1
        elif self.depth and tag not in {
            "br",
            "hr",
            "img",
            "input",
            "meta",
            "link",
            "source",
            "wbr",
            "embed",
            "area",
            "base",
            "col",
            "param",
            "track",
        }:
            self.depth += 1
        if self.depth:
            super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.depth:
            super().handle_endtag(tag)
            self.depth -= 1
            if not self.depth:
                self.flush()

    def handle_startendtag(self, tag, attrs):
        before = self.depth
        self.handle_starttag(tag, attrs)
        if self.depth > before:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.depth:
            super().handle_data(data)


def extract(content: bytes, media: str, url: str) -> tuple[list[Passage], list[str], list[str]]:
    if content.startswith(b"%PDF"):
        try:
            reader = PdfReader(io.BytesIO(content), strict=False)
            if reader.is_encrypted:
                return [], [], ["Encrypted PDF: content not read."]
            if len(reader.pages) > 500:
                return [], [], ["PDF exceeds 500-page extraction limit; not read."]
            passages = []
            empty = 0
            for index, page in enumerate(reader.pages, 1):
                text = " ".join((page.extract_text() or "").split())
                if len(text) < 40:
                    empty += 1
                for offset in range(0, len(text), 3000):
                    passages.append(
                        Passage(
                            f"PDF page {index}, text block {offset // 3000 + 1}",
                            text[offset : offset + 3000],
                        )
                    )
            notes = (
                [
                    f"{empty} PDF pages have little/no extractable text; scanned/graphical content not read."
                ]
                if empty
                else []
            )
            return passages, [], notes
        except (PdfReadError, ValueError, OSError, KeyError) as exc:
            return [], [], [f"PDF extraction failed ({type(exc).__name__}); no OCR performed."]
    if "html" not in media and not urlsplit(url).path.lower().endswith((".htm", ".html")):
        return [], [], ["Unsupported document format; content not read."]
    parser = GuardianArticleHTML() if guardian_article(url) else FilingHTML()
    parser.feed(content.decode("utf-8", errors="replace"))
    parser.flush()
    if guardian_article(url) and not parser.blocks:
        return (
            [],
            [],
            [
                "Public publisher article body unavailable; no paywall, consent or navigation text substituted."
            ],
        )
    return (
        parser.blocks,
        parser.links,
        [
            "HTML locations refer to normalized text blocks, not printed pages. Tables are text-extracted; quantitative analysis uses validated CompanyFacts."
        ],
    )


def filing_rows(submissions: dict) -> list[dict]:
    try:
        recent = submissions["filings"]["recent"]
        fields = ["accessionNumber", "form", "filingDate", "reportDate", "primaryDocument"]
        if len({len(recent[k]) for k in fields}) != 1:
            raise ValueError
        return [dict(zip(fields, values)) for values in zip(*(recent[k] for k in fields))]
    except (KeyError, TypeError, ValueError) as exc:
        raise SECError("SEC document list is malformed; documents unavailable.") from exc


def select_documents(submissions: dict, cik: str, cutoff: str) -> tuple[list[Document], list[str]]:
    rows = [r for r in filing_rows(submissions) if r["filingDate"] <= cutoff]
    annual = sorted(
        [r for r in rows if r["form"] in {"10-K", "20-F"}],
        key=lambda r: r["filingDate"],
        reverse=True,
    )
    if not annual:
        return [], [
            "No 10-K/20-F in SEC recent history. Private/non-SEC filers and older archived history are outside this release."
        ]
    latest = annual[0]
    subsequent = sorted(
        [
            r
            for r in rows
            if r["filingDate"] >= latest["filingDate"]
            and r["form"] in {"10-Q", "10-Q/A", "10-K/A", "20-F/A", "8-K", "8-K/A", "6-K", "6-K/A"}
        ],
        key=lambda r: r["filingDate"],
        reverse=True,
    )
    interims = [r for r in subsequent if r["form"].startswith(("10-Q", "10-K", "20-F"))]
    events = [r for r in subsequent if r not in interims]
    selected = [latest] + interims[:8] + events[:12]
    notes = []
    if len(interims) > 8 or len(events) > 12:
        notes.append(
            f"Document budget: latest annual plus 8 interim/amendment and 12 current reports maximum; {max(0, len(interims) - 8) + max(0, len(events) - 12)} older subsequent reports omitted. Coverage is incomplete."
        )
    if not interims and not events:
        notes.append(
            "No subsequent interim/current filings found in recent SEC history; no claim of exhaustive coverage."
        )
    result = []
    for row in selected:
        accession = row["accessionNumber"].replace("-", "")
        filename = row["primaryDocument"]
        if not re.fullmatch(r"\d{18}", accession) or not re.fullmatch(r"[A-Za-z0-9_.-]+", filename):
            notes.append("Skipped unsupported filing path; coverage incomplete.")
            continue
        result.append(
            Document(
                f"D{len(result) + 1}",
                f"{row['form']} — {row['filingDate']}",
                "annual"
                if row is latest
                else "interim/amendment"
                if row in interims
                else "current report",
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{filename}",
                row["filingDate"],
                row["reportDate"] or "Not specified",
            )
        )
    return result, notes


def retrieve_documents(
    client: EvidenceClient, documents: list[Document], *, refresh=False
) -> list[Document]:
    results = []
    seen = {d.url for d in documents}
    for doc in documents:
        results.append(doc)
        links = read_document(client, doc, refresh=refresh)
        if doc.kind != "current report":
            continue
        exhibits = []
        for href in links:
            url = urljoin(doc.url, href).split("#")[0]
            name = urlsplit(url).path.rsplit("/", 1)[-1]
            if (
                url.rsplit("/", 1)[0] == doc.url.rsplit("/", 1)[0]
                and re.search(
                    r"ex(?:hibit)?[_.-]?99|ex[_.-]?9[. _-]?1|(?:earnings|release|presentation)",
                    name,
                    re.I,
                )
                and url not in seen
            ):
                seen.add(url)
                exhibits.append(url)
        if len(exhibits) > 3:
            doc.limitations.append(
                "Only first 3 relevant exhibits retrieved; additional exhibits not read."
            )
        for url in exhibits[:3]:
            extra = Document(
                f"E{len(results) + 1}",
                f"Exhibit to {doc.title}: {urlsplit(url).path.rsplit('/', 1)[-1]}",
                "earnings/event exhibit",
                url,
                doc.published,
                doc.period,
            )
            read_document(client, extra, refresh=refresh)
            results.append(extra)
    return results


def read_document(client, doc, *, refresh=False):
    doc.passages = []
    doc.tables, doc.table_notes = [], []
    doc.retrieved_at, doc.sha256, doc.cached = "", "", False
    try:
        raw = client.get(doc.url, refresh=refresh)
        doc.retrieved_at, doc.sha256, doc.cached = raw.fetched_at, raw.sha256, raw.cached
        doc.passages, links, notes = extract(raw.content, raw.media_type, doc.url)
        text = " ".join(p.text for p in doc.passages)
        if len(text) < 5000 and re.search(
            r"access denied|request rate threshold exceeded|subscribe to (?:continue|read)|enable javascript to continue",
            text,
            re.I,
        ):
            doc.passages = []
            doc.status = "inaccessible"
            doc.limitations.append(
                "Source returned an access/paywall interstitial; article/document not read."
            )
            return []
        doc.limitations.extend(notes)
        doc.status = "read" if any(len(p.text) > 80 for p in doc.passages) else "unreadable"
        if doc.status == "read" and doc.kind != "news original":
            doc.tables, doc.table_notes = extract_tables(raw.content, raw.media_type)
        if doc.status != "read":
            doc.limitations.append("No substantive extractable text; source was not analysed.")
        return links
    except (SECError, ValueError, OSError) as exc:
        doc.status = "inaccessible"
        doc.limitations.append(str(exc))
        return []


IR_PAGES = {
    "0000320193": "https://investor.apple.com/investor-relations/default.aspx",
    "0000789019": "https://www.microsoft.com/en-us/investor/default",
    "0001985487": "https://ir.kaspi.kz/",
}


def retrieve_ir(client, cik, *, refresh=False):
    """Bounded known-issuer IR discovery; no guessed release or presentation URLs."""
    if cik not in IR_PAGES:
        return [], ["No reviewed investor-relations source configured for this resolved company."]
    landing = Document(
        "IR1",
        "Official investor-relations page",
        "IR discovery",
        IR_PAGES[cik],
        "Not established",
        "Not established",
    )
    links = read_document(client, landing, refresh=refresh)
    result = [landing]
    found = []
    for href in links:
        url = urljoin(landing.url, href).split("#")[0]
        if (
            re.search(r"presentation|earnings.*(?:pdf|release)|results.*pdf", url, re.I)
            and url not in found
        ):
            found.append(url)
    for url in found[:2]:
        document = Document(
            f"IR{len(result) + 1}",
            "IR-linked presentation/earnings document",
            "IR linked document",
            url,
            "Not established",
            "Not established",
        )
        read_document(client, document, refresh=refresh)
        document.limitations.append(
            "Publication date/reporting period not independently established from this link; excluded from date-filtered news conclusions."
        )
        result.append(document)
    notes = [
        "IR discovery is limited to the reviewed issuer landing page and at most 2 directly linked presentation/earnings documents. JavaScript-only links, external CDN hosts and unlinked presentations may be unavailable."
    ]
    if not found:
        notes.append(
            "No directly linked presentation/earnings document discovered on the retrieved IR page; presentation coverage is incomplete."
        )
    return result, notes
