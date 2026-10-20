from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime

from finsight.models import Dataset


@dataclass(frozen=True)
class Company:
    name: str
    ticker: str
    exchange: str
    cik: str
    country: str = "Not established"
    currency: str = "Not established; extraction profile unsupported"
    supported: bool = False
    identity_url: str = "https://www.sec.gov/files/company_tickers_exchange.json"


@dataclass(frozen=True)
class Passage:
    locator: str
    text: str
    heading: str = ""


@dataclass
class Document:
    id: str
    title: str
    kind: str
    url: str
    published: str
    period: str
    retrieved_at: str = ""
    sha256: str = ""
    status: str = "pending"
    passages: list[Passage] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    cached: bool = False


@dataclass
class NewsItem:
    id: str
    title: str
    publisher: str
    url: str
    published: str
    event_date: str | None = None
    category: str = "independent reporting (feed metadata only)"
    access: str = "headline_only; article not read"
    document_id: str | None = None
    duplicate_urls: list[str] = field(default_factory=list)


@dataclass
class Research:
    company: Company
    cutoff: datetime
    news_start: date
    news_end: date
    documents: list[Document] = field(default_factory=list)
    news: list[NewsItem] = field(default_factory=list)
    dataset: Dataset | None = None
    limitations: list[str] = field(default_factory=list)
    stages: dict[str, str] = field(default_factory=dict)
    seconds: dict[str, float] = field(default_factory=dict)
    news_feed: dict = field(default_factory=dict)
    model_usage: dict = field(
        default_factory=lambda: {"mode": "deterministic", "calls": 0, "actual_cost_usd": "0"}
    )

    def serializable(self):
        values = asdict(self)
        values["dataset"] = self.dataset.model_dump(mode="json") if self.dataset else None
        return values
