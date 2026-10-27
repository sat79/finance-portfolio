# Deployment preparation — no deployment performed

The runnable acceptance build remains local. This is an operator checklist, not a provisioned service or approval to deploy. API setup is the final stage; retrieval and deterministic reports must remain usable with `FINSIGHT_ENABLE_MODEL=0`.

## Runtime and configuration

Use Python 3.12, the committed `requirements.txt`/`requirements-lock.txt`, a non-root user and a writable persistent directory. `python -m pip check` and the offline tests must pass after installation. A fresh Linux virtual environment was verified in this task; no container, hosted service, native Mac runtime or production load test was verified.

[Nonsecret environment template](../deploy/environment.example): copy values into the hosting platform's environment settings. Replace the SEC identification placeholder privately. It is not a shell script (the identifying value contains spaces). Do not commit an actual contact address, API credential or cookie secret.

Start with **one application process** behind private access and a TLS reverse proxy supporting WebSockets. A prospective command, not executed as a public deployment:

```bash
python -m streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Keep Streamlit's CORS and XSRF protection enabled. Restrict inbound access to the private gateway; the application does not implement user accounts. The local launcher deliberately binds `127.0.0.1` instead. Use `/_stcore/health` for liveness; a healthy server does not establish source access or research quality.

A starting **assumption**, not a capacity guarantee: one CPU, 2 GiB RAM and at least 2 GiB writable disk for a supervised single-user demo. Measure peak memory/storage under the intended workload before choosing a host. There is no automatic cache-retention policy; define a storage budget and cleanup policy before multi-user operation. Do not remove or rotate the model usage ledger to bypass the one-request/spending limits. Multi-host ledgers are separate budgets; the current lock is not a distributed or provider-account spending control.

## Network requirements

Allow HTTPS to `www.sec.gov`, `data.sec.gov`, `investor.apple.com`, `www.microsoft.com`, `ir.kaspi.kz`, `news.google.com`, and `www.theguardian.com`. Install dependencies through the approved package mirror before running. The application additionally validates bounded URL routes and redirects; a host allowlist alone does not authorize arbitrary URLs. Keep certificate verification enabled. Do not bypass paywalls, widen source routes or replace blocked live results with fixtures.

No model endpoint is needed at this stage. SEC identification, retrieval throttles, response-size limits, date checks, citation eligibility, table abstention and numerical binding stay enabled. Successful network configuration must be proved with actual requests in the target environment.

## Pre-release acceptance and API-last gate

1. On the intended host, verify name → confirmed entity → fresh evidence → opening summary → citation → matching report/manual ZIP/workbook downloads for AAPL, MSFT and KSPI. Confirm a new search removes earlier analysis. Check partial/table/news gaps visibly; retain retrieval timestamps and failures.
2. Review the manual samples and supported table records. Have a second person assess materiality and citation relevance. Fix a concrete launch blocker before expanding coverage. Agree private access, retention, disk monitoring, logs without secrets and rollback to a known commit.
3. Only at the final API stage: separately authorize access; verify maintained model availability/deprecation, supported reasoning settings and current prices; rebuild the shared compact request; inspect its SHA-256, token allowance, 2,400-token ceiling and fixed one-request cap; obtain explicit approval of that exact request. Run once with no automatic retry. Retain failures and reservations. Review actual returned usage, latency, factual support and downloads before deciding on release.

No external model call, billing activation, paid resource, merge or deployment was performed. A provider-generated synthesis and native Mac acceptance remain unverified; this checklist does not imply readiness for unsupervised public release.
