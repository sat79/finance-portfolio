"""Bounded public evidence transport. No arbitrary hosts, redirects or private network URLs."""

import hashlib
import json
import os
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests

from finsight.sec import MAX_RESPONSE_BYTES, SECClient, SECError, _throttle


@dataclass(frozen=True)
class EvidenceResponse:
    content: bytes
    media_type: str
    fetched_at: str
    sha256: str
    cached: bool


class EvidenceClient:
    def __init__(self, sec: SECClient, cache_dir: Path | None = None):
        self.sec = sec
        self.cache_dir = cache_dir or sec.cache_dir / "documents"
        self.attempts = []

    def get(self, url: str, *, refresh=False) -> EvidenceResponse:
        attempt = {"url": url, "attempted_at": datetime.now(timezone.utc).isoformat()}
        self.attempts.append(attempt)
        try:
            result = self._get(url, refresh=refresh)
            attempt.update(
                status="retrieved",
                retrieved_at=result.fetched_at,
                sha256=result.sha256,
                cached=result.cached,
            )
            return result
        except SECError as exc:
            attempt.update(status="failed", reason=str(exc))
            raise

    def _get(self, url: str, *, refresh=False) -> EvidenceResponse:
        parsed = urlsplit(url)
        official = bool(
            re.fullmatch(
                r"https://www\.sec\.gov/Archives/edgar/data/\d+/\d{18}/[A-Za-z0-9_.-]+", url
            )
        )
        news = (
            parsed.scheme == "https"
            and parsed.netloc == "news.google.com"
            and parsed.path == "/rss/search"
        )
        ir = (
            parsed.scheme == "https"
            and parsed.netloc in {"investor.apple.com", "www.microsoft.com", "ir.kaspi.kz"}
            and ".." not in parsed.path
        )
        if not (official or news or ir):
            raise SECError(
                "Evidence URL is outside the supported official filing/public news-feed endpoints."
            )
        key = hashlib.sha256(url.encode()).hexdigest()
        pointer = self.cache_dir / f"{key}.json"
        if not refresh:
            try:
                meta = json.loads(pointer.read_text())
                fetched = datetime.fromisoformat(meta["fetched_at"])
                age = (datetime.now(timezone.utc) - fetched).total_seconds()
                digest = meta["sha256"]
                if re.fullmatch(r"[a-f0-9]{64}", digest) and 0 <= age < (3600 if news else 86400):
                    path = self.cache_dir / f"{digest}.bin"
                    if path.stat().st_size <= MAX_RESPONSE_BYTES:
                        content = path.read_bytes()
                        if hashlib.sha256(content).hexdigest() == digest:
                            return EvidenceResponse(
                                content, meta["media_type"], meta["fetched_at"], digest, True
                            )
            except (OSError, ValueError, TypeError, KeyError):
                pass
        _throttle()
        try:
            headers = {
                "User-Agent": self.sec.user_agent
                if official
                else "FinSightResearch/0.2 (public RSS reader)"
            }
            with self.sec.session.get(
                url, headers=headers, timeout=(5, 25), stream=True, allow_redirects=False
            ) as response:
                if response.status_code != 200:
                    raise SECError(
                        f"Evidence HTTP {response.status_code}; document/feed not read. Retry later."
                    )
                chunks, size = [], 0
                for chunk in response.iter_content(65536):
                    size += len(chunk)
                    if size > MAX_RESPONSE_BYTES:
                        raise SECError("Evidence exceeds 25 MiB; not read.")
                    chunks.append(chunk)
                content = b"".join(chunks)
                media = response.headers.get("Content-Type", "").split(";")[0]
        except requests.RequestException as exc:
            raise SECError(
                "Evidence connection failed; coverage is incomplete. No stale fallback used."
            ) from exc
        digest = hashlib.sha256(content).hexdigest()
        fetched = datetime.now(timezone.utc).isoformat()
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            suffix = f".{os.getpid()}.{threading.get_ident()}.tmp"
            blob = self.cache_dir / f"{digest}.bin"
            temp = blob.with_suffix(suffix)
            temp.write_bytes(content)
            temp.replace(blob)
            temp = pointer.with_suffix(suffix)
            temp.write_text(
                json.dumps(
                    {"url": url, "sha256": digest, "fetched_at": fetched, "media_type": media}
                )
            )
            temp.replace(pointer)
        except OSError as exc:
            raise SECError(
                "Evidence cache is not writable; set FINSIGHT_CACHE_DIR to a writable directory."
            ) from exc
        return EvidenceResponse(content, media, fetched, digest, False)
