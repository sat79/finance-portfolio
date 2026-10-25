# Research a company

Install and launch using the [Mac guide](mac-setup.md) or README. From this project directory, activate `.venv`, set your real identifying `SEC_USER_AGENT` locally, then run:

```bash
bash scripts/start.sh
```

1. Leave **Company research** selected. Enter **Kaspi.kz**, **Microsoft**, or **Apple** and click **Find company**. Confirm the legal entity and ticker; Apple can match multiple companies. Research is unavailable until an ambiguous result is selected.
2. Review the financial-coverage label. Adjust the default 90-day news publication window if needed, then click **Research selected company**. Stages retain completed evidence when a later source fails. The outcome is complete, partial or failed based on actual substantive coverage; a failed run never displays successful completion.
3. Read the report’s business model, annual trends, cash/position limitations, management quotations, developments, risks and conclusion. Review the warnings alongside figures. Interpretations are questions for investigation, not predictions or verified investment conclusions.
4. Open **Evidence & coverage** to inspect document dates, URLs, hashes, retrieval times, unread documents and news access. HTML citations identify normalized text blocks; PDFs identify pages. Up to three accessible original/official sources supply selected text. A headline remains discovery-only when source text was not read. Event dates remain unknown when the source does not establish them.
5. Use **Download research** for Markdown or the ZIP evidence pack. Figures, formulas, input references and review warnings remain available in the financial workbook. The bundle also contains coverage.json and the exact model-evidence.json payload, with no model call required. Financial extraction covers only KSPI/AAPL/MSFT. NVIDIA or another resolved company can have a document report with a clear quantitative coverage gap.

If a search returns no match, try an official ticker or legal name. A private company or non-US-only listing may not appear. If a source is blocked, the app displays the failure; it never replaces it with fictional data. Changing the company/date controls does not silently relabel an existing report: research again to apply them. Starting a new search clears the old report.

## Optional model connection

The report above requires no model. A ChatGPT subscription is not API access. No call occurs until API configuration and the per-request approval checkbox are both present. Configure locally only if you choose paid generation:

- `FINSIGHT_OPENAI_API_KEY`: your API credential via the managed environment's secure binding for `api.openai.com`; never commit it or paste it into a report. Local `OPENAI_API_KEY` remains a fallback. The managed environment reserves the `OPENAI_` prefix, so use the FinSight name for that binding.
- `FINSIGHT_ENABLE_MODEL=1` and `FINSIGHT_MODEL`: opt in and choose an available Responses API model.
- `FINSIGHT_INPUT_USD_PER_MILLION`, `FINSIGHT_OUTPUT_USD_PER_MILLION`: current prices for that model, checked against the provider’s pricing.
- `FINSIGHT_MODEL_CAP_USD`: positive cumulative cap for this local ledger.

The optional call requires access to `api.openai.com`; that paid destination is not required or enabled by the default workflow. Cloud proxy credential configuration may reserve names beginning `OPENAI_`; do not assume a local variable is an injectable cloud credential. No cloud API binding has been provisioned in this task.

The UI shows a conservative byte-based input token allowance, 1,200 output-token maximum and estimated reservation before approval. This acceptance pilot allows **one request per shared ledger, with no automatic retries**, even if the remaining dollar budget would permit more. Reservations persist in `.cache/sec/model-usage.jsonl` (or `FINSIGHT_CACHE_DIR`) even after failures, since a timed-out request may still incur a charge. Do not remove this ledger to bypass either limit. Linux/macOS file locking prevents concurrent processes sharing a ledger from exceeding it. Different ledgers/machines are separate budgets; this is not an account-wide provider billing cap. User-entered prices can be wrong, so the reservation is not a billing guarantee.

After generation, **Application-generated analysis** labels the provider output separately from the deterministic report and earlier assistant-written exercise. Inspect cited excerpts and bound financial records, then download the combined evidence/analysis ZIP. Provider usage, measured latency, output text and failures remain in the local usage ledger. Incomplete or invalid outputs do not become accepted analysis; the original report remains available. See the [current pilot preparation and blockers](review-artifacts/2026-10-25-mvp/README.md).

The output displays provider token usage when returned. Actual billed cost is not inferred. Numerical claims must match an exact supplied metric/period/currency/value/source record and are rendered deterministically. Management explanations must be verbatim cited text. Interpretations need exact supporting excerpts but semantic relevance, truth and causation are not automatically verified; human review remains necessary. The downloaded optional narrative includes source limitations and financial warnings and remains separate from the deterministic research evidence pack.
