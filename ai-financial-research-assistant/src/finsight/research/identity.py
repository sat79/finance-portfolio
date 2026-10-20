"""SEC directory discovery is deliberately broader than reviewed financial coverage."""

import re
from dataclasses import replace

from finsight.profiles import profile_for
from finsight.research.models import Company
from finsight.sec import SUPPORTED, SECClient, SECError

DIRECTORY = "https://www.sec.gov/files/company_tickers_exchange.json"
US_STATES = set(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
)


def normalise(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def search(directory: dict, query: str) -> list[Company]:
    query = normalise(query.strip())
    if not query or len(query) > 100:
        raise SECError("Enter a company name or ticker (1–100 characters).")
    try:
        fields = directory["fields"]
        if not {"cik", "name", "ticker", "exchange"} <= set(fields):
            raise ValueError
        matches = []
        for row in directory["data"]:
            if len(row) != len(fields):
                raise ValueError
            item = dict(zip(fields, row))
            if query == normalise(item["ticker"]) or all(
                word in normalise(item["name"]).split() for word in query.split()
            ):
                cik = str(int(item["cik"])).zfill(10)
                supported = any(cik == known[1] for known in SUPPORTED.values())
                matches.append(
                    Company(
                        item["name"],
                        item["ticker"],
                        item["exchange"] or "Not listed",
                        cik,
                        currency=profile_for(cik).currency
                        if supported
                        else "Not established; extraction profile unsupported",
                        supported=supported,
                    )
                )
        return sorted(
            matches,
            key=lambda c: (
                normalise(c.ticker) != query,
                normalise(c.name) != query,
                c.name,
                c.ticker,
            ),
        )
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise SECError("Official company directory has an unsupported schema.") from exc


def resolve_details(company: Company, submissions: dict) -> Company:
    if str(int(submissions.get("cik", -1))).zfill(10) != company.cik:
        raise SECError("Resolved company identity disagrees with SEC submissions.")
    address = submissions.get("addresses", {}).get("business", {})
    state = address.get("stateOrCountry", "")
    country = (
        "United States"
        if state in US_STATES
        else address.get("stateOrCountryDescription") or "Not established"
    )
    return replace(
        company,
        name=submissions.get("name") or company.name,
        country=country,
        identity_url=f"https://data.sec.gov/submissions/CIK{company.cik}.json",
    )


def find_companies(client: SECClient, query: str) -> list[Company]:
    return search(client._request(DIRECTORY).data, query)
