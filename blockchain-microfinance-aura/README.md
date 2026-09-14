# Blockchain microfinance and AURA
**Financial question:** What does a financial-inclusion proposal need beyond lower transaction costs?

**Finding:** AURA provides a useful conceptual checklist. The new audit checks arithmetic and assumptions; empirical validation remains outstanding.

[Read the research note](reports/Research-Note.md) · [Data and provenance](data/README.md) · [Machine-readable results](reports/results.json)

## Reproduce
Extract the project and open a terminal inside its folder. Tested with Python 3.12.14 on Linux. Other operating systems have not been verified. Create an isolated environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/verify_package.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/analyse.py
```

On Windows, create the environment with `py -3.12 -m venv .venv` and use `.venv\Scripts\python.exe` instead of `.venv/bin/python`. These Windows instructions are provided for convenience, not a claim of platform testing.

Install requires package-network access. Analysis runs locally against the included CSVs with no network, credentials or API key. Defaults resolve relative to the script, so it also runs from another working directory. `--output /path/to/results` writes a separate result set. Run the package verifier **before** regenerating outputs; checksums cover the distributed baseline and will change after edits or environment-dependent chart rendering.

## Repository structure
- `data/`: supplied CSVs, provenance and input hashes.
- `src/analyse.py`: calculations and report/chart generation.
- `tests/`: mathematical, input and chronological-control checks.
- `reports/`: research note, reproducible results and chart.
- `requirements.txt`: pinned direct numerical dependencies.
- `requirements-lock.txt`: full tested environment, shared across these three new projects.

## Scope and authorship
Portfolio extension, September 2026. This is finance analysis with inspectable code, not a production application. Read the research note before interpreting the outputs. Original academic research and newly written code are distinguished explicitly. Limitations are part of the analysis.
