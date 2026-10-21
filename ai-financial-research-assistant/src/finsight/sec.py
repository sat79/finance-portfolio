"""Official SEC JSON only; bounded requests, identified clients and explicit caching."""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import requests

SUPPORTED = {
    "KSPI": ("Kaspi.kz", "0001985487"),
    "AAPL": ("Apple Inc.", "0000320193"),
    "MSFT": ("Microsoft Corporation", "0000789019"),
}
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
MAX_RESPONSE_BYTES = 25 * 1024 * 1024
_RATE_LOCK = threading.Lock()
_LAST_REQUEST = 0.0


class SECError(ValueError):
    """Actionable external-data failure; never silently falls back to demo data."""


def _decode(payload: str) -> dict:
    def reject_constant(value):
        raise ValueError("Non-finite JSON number.")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key.")
            result[key] = value
        return result

    return json.loads(
        payload,
        parse_float=Decimal,
        parse_constant=reject_constant,
        object_pairs_hook=unique_object,
    )


@dataclass(frozen=True)
class Response:
    data: dict
    fetched_at: datetime
    cached: bool
    sha256: str


def _throttle():
    global _LAST_REQUEST
    with _RATE_LOCK:
        delay = 1.0 - (time.monotonic() - _LAST_REQUEST)
        if delay > 0:
            time.sleep(delay)
        _LAST_REQUEST = time.monotonic()


class SECClient:
    def __init__(
        self,
        user_agent: str | None = None,
        cache_dir: Path | None = None,
        session=None,
        ttl_seconds: int = 86400,
    ):
        self.user_agent = user_agent or os.environ.get("SEC_USER_AGENT", "")
        if (
            len(self.user_agent) > 250
            or "\n" in self.user_agent
            or "\r" in self.user_agent
            or not re.search(r"[^\s@]+@[^\s@]+\.[^\s@]+", self.user_agent)
        ):
            raise SECError(
                "Set SEC_USER_AGENT locally to an application name and real contact email."
            )
        self.cache_dir = cache_dir or Path(os.environ.get("FINSIGHT_CACHE_DIR", ".cache/sec"))
        self.session = session or requests.Session()
        self.ttl_seconds = ttl_seconds
        self.attempts = []

    def _request(self, url: str, refresh=False) -> Response:
        attempt = {"url": url, "attempted_at": datetime.now(timezone.utc).isoformat()}
        self.attempts.append(attempt)
        try:
            response = self._fetch(url, refresh)
            attempt.update(
                status="retrieved",
                retrieved_at=response.fetched_at.isoformat(),
                cached=response.cached,
                sha256=response.sha256,
            )
            return response
        except SECError as exc:
            attempt.update(status="failed", reason=str(exc))
            raise

    def _fetch(self, url: str, refresh=False) -> Response:
        allowed = url in {
            TICKERS_URL,
            "https://www.sec.gov/files/company_tickers_exchange.json",
        } or re.fullmatch(
            r"https://data\.sec\.gov/(api/xbrl/companyfacts|submissions)/CIK\d{10}\.json", url
        )
        if not allowed:
            raise SECError("Only supported official SEC endpoints may be requested.")
        path = self.cache_dir / (hashlib.sha256(url.encode()).hexdigest() + ".json")
        if path.exists() and not refresh:
            try:
                saved = json.loads(path.read_text())
                fetched = datetime.fromisoformat(saved["fetched_at"])
                age = (datetime.now(timezone.utc) - fetched).total_seconds()
                payload = saved["payload"]
                if (
                    0 <= age < self.ttl_seconds
                    and isinstance(payload, str)
                    and len(payload.encode()) <= MAX_RESPONSE_BYTES
                    and hashlib.sha256(payload.encode()).hexdigest() == saved["sha256"]
                ):
                    data = _decode(payload)
                    if isinstance(data, dict):
                        return Response(data, fetched, True, saved["sha256"])
            except (ValueError, KeyError, TypeError, OSError):
                pass  # Corrupt/expired caches are re-fetched, never used as stale data.
        for attempt in range(3):
            _throttle()
            try:
                with self.session.get(
                    url,
                    headers={"User-Agent": self.user_agent, "Accept": "application/json"},
                    timeout=(5, 25),
                    allow_redirects=False,
                    stream=True,
                ) as response:
                    status = response.status_code
                    if status == 429 or 500 <= status <= 599:
                        if attempt < 2:
                            retry = response.headers.get("Retry-After", "")
                            delay = min(max(float(retry), 1), 10) if retry.isdigit() else 2**attempt
                            time.sleep(delay)
                            continue
                        raise SECError(
                            f"SEC HTTP {status}; retry later. No stale or demo data substituted."
                        )
                    if status != 200:
                        raise SECError(
                            f"SEC HTTP {status}. Check SEC identification and network access; "
                            "use CSV or the explicitly labelled synthetic example meanwhile."
                        )
                    chunks, size = [], 0
                    for chunk in response.iter_content(65536):
                        size += len(chunk)
                        if size > MAX_RESPONSE_BYTES:
                            raise SECError("SEC response exceeds the 25 MiB safety limit.")
                        chunks.append(chunk)
                    payload = b"".join(chunks).decode("utf-8")
                    data = _decode(payload)
                    if not isinstance(data, dict):
                        raise SECError("Unexpected SEC response: expected a JSON object.")
            except (requests.Timeout, requests.ConnectionError) as exc:
                if attempt < 2:
                    time.sleep(2**attempt)
                    continue
                raise SECError(
                    "SEC connection failed after three attempts. Check network access "
                    "to www.sec.gov and data.sec.gov. No fallback was substituted."
                ) from exc
            except (ValueError, UnicodeError) as exc:
                if isinstance(exc, SECError):
                    raise
                raise SECError("SEC returned malformed JSON or text.") from exc
            except requests.RequestException as exc:
                raise SECError("SEC request failed; check network access and retry later.") from exc
            fetched = datetime.now(timezone.utc)
            digest = hashlib.sha256(payload.encode()).hexdigest()
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                # Cache only public SEC JSON, never request headers or uploaded CSVs.
                temporary = path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
                temporary.write_text(
                    json.dumps(
                        {"payload": payload, "sha256": digest, "fetched_at": fetched.isoformat()}
                    )
                )
                temporary.replace(path)
            except OSError as exc:
                raise SECError(
                    "SEC cache is not writable; set FINSIGHT_CACHE_DIR to a writable path."
                ) from exc
            return Response(data, fetched, False, digest)
        raise SECError("SEC request exhausted retries.")

    def load(self, ticker: str, refresh=False):
        from finsight.selection import select_annual

        ticker = ticker.strip().upper()
        if ticker not in SUPPORTED:
            raise SECError("SEC coverage is KSPI, AAPL and MSFT only.")
        mapping = self._request(TICKERS_URL, refresh)
        matches = [
            v for v in mapping.data.values() if isinstance(v, dict) and v.get("ticker") == ticker
        ]
        try:
            if len(matches) != 1:
                raise SECError("Ticker did not resolve uniquely in the official SEC directory.")
            cik = str(int(matches[0]["cik_str"])).zfill(10)
            if cik != SUPPORTED[ticker][1]:
                raise SECError("SEC company identity changed; mapping requires analyst review.")
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, SECError):
                raise
            raise SECError("Malformed company identifier in SEC directory.") from exc
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        facts = self._request(facts_url, refresh)
        submissions = self._request(submissions_url, refresh)
        return select_annual(
            facts.data,
            submissions.data,
            cik=cik,
            origin="sec_cache"
            if any(r.cached for r in [facts, submissions, mapping])
            else "sec_live",
            fetched_at=min(r.fetched_at for r in [facts, submissions, mapping]),
            source_hashes={facts_url: facts.sha256, submissions_url: submissions.sha256},
        )
