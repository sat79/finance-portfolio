import json
from unittest.mock import Mock

import pytest
import requests

from finsight.sec import SECClient, SECError

URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"


class Reply:
    def __init__(self, status=200, body=b'{"ok": true}', headers=None):
        self.status_code = status
        self.body = body
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def iter_content(self, size):
        return [self.body]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("finsight.sec._throttle", lambda: None)
    monkeypatch.setattr("finsight.sec.time.sleep", lambda delay: None)
    return SECClient("FinSight tests contact@example.org", tmp_path, session=Mock())


def test_required_identification_and_no_arbitrary_urls(client):
    with pytest.raises(SECError, match="SEC_USER_AGENT"):
        SECClient("anonymous")
    with pytest.raises(SECError, match="endpoints"):
        client._request("http://localhost/secrets")
    with pytest.raises(SECError, match="endpoints"):
        client._request(URL + "?redirect=evil")


def test_cache_request_headers_timeout_and_force_refresh(client):
    client.session.get.return_value = Reply()
    first = client._request(URL)
    second = client._request(URL)
    assert not first.cached and second.cached
    assert first.sha256 == second.sha256 and first.fetched_at == second.fetched_at
    assert client.session.get.call_count == 1
    options = client.session.get.call_args.kwargs
    assert options["timeout"] == (5, 25) and options["allow_redirects"] is False
    assert "@" in options["headers"]["User-Agent"]
    client._request(URL, refresh=True)
    assert client.session.get.call_count == 2
    cache = next(client.cache_dir.glob("*.json")).read_text()
    assert "contact@example.org" not in cache


def test_expired_cache_does_not_hide_failure(client):
    client.session.get.return_value = Reply()
    client._request(URL)
    client.ttl_seconds = 0
    client.session.get.return_value = Reply(403)
    with pytest.raises(SECError, match="HTTP 403"):
        client._request(URL)


def test_corrupt_cache_refetched(client):
    client.session.get.return_value = Reply()
    client._request(URL)
    next(client.cache_dir.glob("*.json")).write_text("{}")
    assert not client._request(URL).cached


def test_retry_rate_limit_and_server_error(client):
    client.session.get.side_effect = [Reply(429, headers={"Retry-After": "2"}), Reply(503), Reply()]
    assert client._request(URL).data == {"ok": True}
    assert client.session.get.call_count == 3


def test_connection_failure_explicit(client):
    client.session.get.side_effect = requests.ConnectionError("proxy unavailable")
    with pytest.raises(SECError, match="three attempts"):
        client._request(URL)
    assert client.session.get.call_count == 3


@pytest.mark.parametrize(
    "reply", [Reply(302), Reply(403), Reply(200, b"<html>blocked</html>"), Reply(200, b"[]")]
)
def test_redirect_denial_or_malformed_data_rejected(client, reply):
    client.session.get.return_value = reply
    with pytest.raises(SECError):
        client._request(URL)


def test_size_limit(client, monkeypatch):
    monkeypatch.setattr("finsight.sec.MAX_RESPONSE_BYTES", 5)
    client.session.get.return_value = Reply()
    with pytest.raises(SECError, match="safety limit"):
        client._request(URL)


def test_supported_company_identity_and_pipeline(client, raw, submissions):
    # Transport/selection integration uses FICTIONAL values labelled in fixture; not live validation.
    raw["cik"] = 320193
    submissions["cik"] = "0000320193"
    client.session.get.side_effect = [
        Reply(body=json.dumps({"0": {"ticker": "AAPL", "cik_str": 320193}}).encode()),
        Reply(body=json.dumps(raw).encode()),
        Reply(body=json.dumps(submissions).encode()),
    ]
    data = client.load("aapl")
    assert len(data.periods) == 3 and data.cik == "0000320193"
    assert data.origin == "sec_live"  # mocked transport path only
    assert all(f.source_url.startswith("https://www.sec.gov/Archives/") for f in data.selected)
    assert len(data.source_hashes) == 2


def test_unknown_ticker_and_mismatched_cik(client):
    with pytest.raises(SECError, match="AAPL and MSFT"):
        client.load("JPM")
    client.session.get.return_value = Reply(body=b'{"0":{"ticker":"AAPL","cik_str":99}}')
    with pytest.raises(SECError, match="identity changed"):
        client.load("AAPL")


def test_source_decimals_and_duplicate_keys(client):
    from decimal import Decimal

    client.session.get.return_value = Reply(body=b'{"value":1.1234567890}')
    assert client._request(URL).data["value"] == Decimal("1.1234567890")
    assert str(client._request(URL).data["value"]) == "1.1234567890"
    client.session.get.return_value = Reply(body=b'{"value":1,"value":2}')
    with pytest.raises(SECError, match="malformed"):
        client._request(URL, refresh=True)


def test_timeout_retries_bounded(client):
    client.session.get.side_effect = requests.Timeout("timeout")
    with pytest.raises(SECError):
        client._request(URL)
    assert client.session.get.call_count == 3
