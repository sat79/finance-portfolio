# Run FinSight on your Intel Mac

This guide runs FinSight locally on an Intel Mac, without hosting or a model API. On 26 October 2026 we verified a **fresh Linux/Python 3.12 virtual environment**, the pinned install, dependency consistency, the offline suite and the real launcher/browser journey. We also downloaded every pinned dependency for Python 3.12 / Intel macOS 12 (including the PDF parser). Wheel availability is **not a native Mac installation test**. You must verify installation, Chrome and downloaded files on your Mac; macOS older than 12 is untested.

The reviewed company-research scope is **AAPL, MSFT and KSPI**. Keep API synthesis disabled throughout this walkthrough. See the [current handover](review-artifacts/2026-10-26-api-last/README.md) for the exact checks and limitations.

## 1. Check your computer and Python

Open **Applications → Utilities → Terminal**. Run each line separately:

```bash
uname -m
sw_vers -productVersion
python3.12 --version
```

The first command should show `x86_64` on your Intel Mac; the second shows your macOS version. The third should show `Python 3.12.x`. If it says “command not found”, also try `python3 --version`. If that is already 3.12, substitute `python3` for `python3.12` below. Do not change Apple's system Python.

If Python 3.12 is missing:

- If you already use Homebrew, run `brew install python@3.12`, then `python3.12 --version`. This provides the maintained 3.12 patch version without replacing the system Python.
- Otherwise, the official [Python 3.12.10 macOS universal2 installer](https://www.python.org/downloads/release/python-31210/) supports Intel. Download the macOS installer, run it, reopen Terminal, and check `python3.12 --version`. Python 3.12.10 is the last 3.12 release with a python.org binary installer; later 3.12 security releases are source-only there. Prefer an up-to-date 3.12 installation when available. You do not need to build Python from source for this walkthrough.

For a python.org installation, open its **Install Certificates.command** in `/Applications/Python 3.12/` once. This installs the certificates used for HTTPS. Do not disable certificate verification to solve connection errors.

## 2. Get the existing feature branch

If you have Git already, run:

```bash
cd ~/Documents
git clone --branch feat/finsight-research-mvp --single-branch https://github.com/sat79/finance-portfolio.git
cd finance-portfolio/ai-financial-research-assistant
git branch --show-current
```

These commands download the existing project, enter the app folder, and confirm `feat/finsight-research-mvp`. They do not merge the PR. If `finance-portfolio` already exists, do not clone over it. Enter that existing checkout, run `git status`, and preserve any local changes before switching branches.

If Git is unavailable, you can avoid installing developer tools: in Chrome open the [feature branch](https://github.com/sat79/finance-portfolio/tree/feat/finsight-research-mvp), choose **Code → Download ZIP**, and unzip it in Downloads. Rename the extracted folder to `finance-portfolio-finsight`, then run:

```bash
cd ~/Downloads/finance-portfolio-finsight/ai-financial-research-assistant
```

Use either Git or ZIP, not both. A ZIP has no Git history, but runs the same app.

## 3. Install into an isolated environment

Run from `ai-financial-research-assistant`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install -r requirements.txt
python -m pip check
python -m pytest -q
```

`.venv` keeps this app's dependencies separate from your other portfolio projects. Activation makes `python` use that environment. Installation uses the committed version lock; `pip check` checks dependency compatibility; the offline suite should report **232 passed** at this revision. Installation needs Internet access; these tests do not need SEC access. Do not use `sudo pip`.

If pip reports no compatible distribution, check Python is 3.12, `uname -m` is `x86_64`, and macOS is at least 12. Keep the exact error for troubleshooting rather than randomly changing dependency versions. A newer macOS version should not be installed solely on the strength of this guide.

## 4. Start with local SEC identification

```bash
export FINSIGHT_ENABLE_MODEL=0
bash scripts/start.sh
```

The launcher checks the existing environment and asks for your contact email if `SEC_USER_AGENT` is unset. Enter your real email. It constructs `FinSightAI <email>` for the SEC request header, only for this running process; it does not save the address or put it in Git. Press Enter without an email to use the fictional example or CSV only. The email is contact identification, not a paid API key. It is sent to the SEC when fetching data.

The script can be run from a fresh Terminal without activating `.venv`; it uses the app's own Python. It does not install packages or automatically execute `.env` files.

Alternatively, configure the current Terminal session explicitly, then launch:

```bash
read -r "finsight_contact?Your SEC contact email: "
export SEC_USER_AGENT="FinSightAI $finsight_contact"
unset finsight_contact
export FINSIGHT_ENABLE_MODEL=0
bash scripts/start.sh
```

The `read` prompt above uses the default macOS **zsh** shell and keeps the entered email out of shell history. For a bash Terminal, use `read -r -p 'Your SEC contact email: ' finsight_contact` instead. Do not paste the address into source code. If you previously created a trusted ignored `.env` yourself, `source .env` is an optional alternative; it executes shell commands, so only source your own file.

## 5. Open Chrome and try an analysis

Leave Terminal running. In Chrome, type `http://localhost:8501` into the address bar (on **your Mac**). If Streamlit prints a different port, use that port.

1. Leave **Company research** selected. Enter **Apple**, click **Find company**, and select **AAPL — Apple Inc.** from the possible matches. Confirm the legal name before clicking **Research selected company**.
2. For a live check, enable **Refresh evidence from sources**. Read the resulting complete/partial/failed status. Successful retrieval does not mean all financial tables were supported. No fixture replaces a failed source request.
3. Read **Opening summary**, then the evidence appendix. Keep annual calculations separate from interim figures and company explanations. Open **Evidence & coverage → Inspect citation register**; follow an SEC source link and compare the quoted passage and reporting period.
4. In **Download research**, download the Markdown report, evidence ZIP and compact manual-synthesis ZIP. Unzip the evidence bundle and inspect `coverage.json`, `citations.json` and `financial-analysis.xlsx`. The workbook does not require the app to have an API key; opening it in Excel or another spreadsheet program is a local check you must perform.
5. For manual ChatGPT use, unzip the compact pack and use `evidence.json` with `instructions.txt`. This sends nothing automatically. Label any resulting analysis as manual and review its citations. The app does not import chat responses.
6. Search **Microsoft**, then **Kaspi.kz**. Confirm **MSFT** and **KSPI**. Before running each new search, verify the previous report and analysis have disappeared. Repeat the source/citation/download checks. Kaspi independent-news coverage remains unavailable in the reviewed route; do not treat discovery headlines as read articles.
7. Leave the optional model section disabled. Automatic provider narrative is the final, separately approved stage, not a prerequisite for this workflow.

For a network-independent check, choose **Synthetic example → Load fictional example**. FY2023 revenue is 1,200 USD and operating margin is 8%. Those numbers are fictional.

## 6. Stop and restart

Click the Terminal window running Streamlit and press **Control+C** once. Closing Chrome alone does not stop the Python server. If you activated the environment manually, `deactivate` restores your Terminal's normal Python selection.

Next time, enter the project folder and run `bash scripts/start.sh` again. Do not reinstall dependencies each time. Restart after updating Python packages or application code. If port 8501 is occupied, stop your earlier FinSight session or run `bash scripts/start.sh --server.port 8502`, then use that port in Chrome.

For SEC 403/network errors, check identification, Internet access, and the displayed message. SEC destinations are `www.sec.gov` and `data.sec.gov`; the bounded research route also uses the reviewed company IR sites, Google News discovery and `www.theguardian.com` for selected original articles. See the deployment guide for the exact current allowlist. For 429 responses, wait before retrying; repeated refresh clicks will not help. For “cache not writable”, launch from your own project folder or set `FINSIGHT_CACHE_DIR` to a directory you own. Share the error message and Python/macOS versions for troubleshooting, but leave your email and `.env` out of screenshots/logs.
