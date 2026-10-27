# Automated analytical usefulness — 24 October 2026

The report now opens with four or five evidence-backed Key findings in the three reviewed companies. Kaspi's quarterly group result, operating drivers and Stage 3 restructured-loan disclosure are selected automatically, with their original citations and nearby context. This is a more useful starting point for research; it is not a completed valuation or an evaluated semantic synthesis system.

Read or download the **complete reports and production-app evidence ZIPs** from the [review artifact index](review-artifacts/2026-10-24/README.md). The ZIPs contain the report, full citation/model evidence registers, research snapshot, source/news registers, coverage and financial workbook. They are review-branch files, not a deployment. The [23 October analyst memo](kspi-analytical-review-2026-10-23.md) and its citation register remain unchanged as the review benchmark.

## Why the previous selection missed useful evidence

The previous recent-document selector ranked a few paragraphs by generic keyword matches, excluded passages shorter than 80 characters, and took period context from the first matching blocks in a document. It could prefer accounting-policy text, miss Microsoft's 69-character revenue bullet, omit a credit-risk stock disclosure without an explicit credit-risk category, and quote a quarterly result without its nearby heading. A later short news excerpt could also overwrite the full selected quote for the same citation.

The revised selector ranks results, credit risk, operating drivers, management explanations and capital actions separately. It excludes common boilerplate, admits substantive short result bullets, and retains up to six primary passages per dated recent document. It carries up to three nearby period/heading/unit passages per selection, quoting context rather than assigning a numeric reporting period from proximity. Selected primary text is at most 1,600 characters and is not truncated; exact document/block citations, locators, source URLs, hashes and retrieval timestamps remain available. Quarterly and year-to-date wording, reported/constant-currency qualifiers, segment names, GAAP/non-GAAP distinctions and group/parent attribution stay in the source text.

Repeated measures in highlights and segment discussion are deduplicated. Equivalent undated supplements are quoted once with their alternate document IDs retained; undated material still cannot displace dated latest evidence. The limit remains two dated recent documents and at most two single-passage supplementary documents. Annual extraction and the Kaspi financial-group safeguards are unchanged.

Key findings prefer latest reported results, one annual calculation finding, operating drivers, credit risk and explanations, with capital actions filling available space. Each finding contains exact reported statements or attributed management explanations, existing deterministic calculations, and an explicit unresolved question. There is no generated causal bridge, no forced minimum when evidence is absent, and no normalization of quarterly prose into financial observations. Sentence labels use lexical cues, not evaluated semantic classification.

## Concrete before/after evaluation

An uncached three-company baseline was retrieved on 24 October at 09:17 UTC using the old selector. Both implementations then rendered **the identical saved source snapshots**; this paired rendering is an offline comparison, not another live retrieval. The [machine-readable comparison](evidence/selection-evaluation-2026-10-24.json) records cutoffs, snapshot hashes, exact target quotes and report/model presence. The review-only target IDs are in `scripts/evaluate_selection.py`; application selection has no company-specific target IDs and does not import the memo.

| Company / evidence | Before | After / exact supporting citation |
|---|---|---|
| Kaspi consolidated quarterly result | Missing from selected report/model evidence | 2Q revenue +15% to KZT1.1tn; adjusted EBITDA +5%; net income stable at KZT259bn. Full source paragraph and 2Q heading retained: `E7:B24`, context `E7:B5`/`E7:B4`. Management's Türkiye/funding explanation remains attributed. |
| Kaspi volume and monetization | Useful details omitted | Constant-currency GMV +28%, purchases +33% (`E7:B9`); VAS +49%, take rate +160bps to 16.1%, constant-currency e-Commerce revenue +35% (`E7:B74`). The latter repeats the memo's B11 measures in fuller segment prose and is selected once. |
| Kaspi credit and funding | Funding paragraph present; Stage 3 stock absent | Funding explanation `E7:B19` retained. `E5:B2151` added: restructured Stage 3 gross carrying amount KZT145,302m at 31 Dec 2025 and KZT178,567m at 30 Jun 2026. No assertion that this subset is total NPLs, a loss rate or a quarterly flow. |
| Apple results and explanation | Quarterly result already present; interim explanation missing | `E7:B6` retained with fiscal Q3 end date and tariff-refund qualifiers. `D2:B624` added: product mix/tariff refunds and higher costs, including memory, for both Q3 and first nine months. No separation into unsupported quarterly contributions. |
| Microsoft short results and drivers | Revenue bullet omitted; net income and discrete items already present | `E5:B6` added: $90bn revenue, +18% reported / +17% constant currency. `E5:B10` GAAP/non-GAAP income and `E5:B15` discrete EPS items retained. Intelligent Cloud `E5:B72` added, retaining segment scope and +32% reported / +31% constant-currency growth. |

All **11/11** chosen target passages are now in both report and model evidence, compared with **4/11** before. This small, hand-selected benchmark guided development; it is not held-out evaluation, exhaustive recall, or proof of analytical/semantic accuracy.

| Company | Findings | Primary recent passages | Unique recent citations including context | Full model JSON bytes, before → after |
|---|---:|---:|---:|---:|
| Kaspi | 5 | 8 across two dated documents | 13 | 201,754 → 135,407 |
| Apple | 4 | 4 | 6 | 185,062 → 150,183 |
| Microsoft | 5 | 7 including one undated supplement | 9 | 190,288 → 159,948 |

The smaller payload stores recent passages once in the citation register and deduplicates warning strings into a referenced warning registry. Full structured news records, financial observations, deterministic calculations and warnings remain supplied. Recent-document references resolve to actual quoted contents, not just URLs. The complete model package has bounded selection counts, not a universal byte/token cap; an optional smaller pilot packet is separate.

## Fresh production-app validation

After the changes, real Chromium journeys used `app/main.py`: enter company name, confirm entity, refresh sources, read Key findings/report, inspect citations, and download/open the evidence ZIP and financial workbook. No workflow replacement, historical replay or paid model was used. Exact fresh cutoffs and request outcomes are in the [browser acceptance record](review-artifacts/2026-10-24/browser-acceptance.json) and each ZIP's `research-evidence.json`. Successful source requests were checked to have `cached=false`.

| Company | Official documents read | Annual observations | Independent article text | Key findings | Outcome |
|---|---:|---:|---|---:|---|
| Apple | 16/16 | 40 | One selected original Guardian article read and cited | 4 | Complete bounded checks |
| Microsoft | 8/8 | 40 | One selected original Guardian article read and cited | 5 | Complete bounded checks |
| Kaspi.kz | 21/21, including IR landing page | 27 | Feed retrieved; no matching article | 5 | Partial |

The managed network status reported the configured custom hosts including Guardian but enforcement state remained unknown. Actual successful requests establish access for these runs; saved configuration alone is not treated as proof. No policy change or bypass was needed. Microsoft's verified canonical IR endpoint remains in use.

**194 tests pass**, Ruff lint and formatting pass (73 Python files), and dependency consistency passes. Nine new regression cases cover short results/context, credit stock versus collection-flow dates, driver deduplication, insufficient evidence, explanation/source-span labels, quote preservation, warning/calculation references, supplementary duplicates and bundle excerpts. Existing metric/period/currency/source claim checks, negative citation tests, date ranking, financial controls and spend guards continue to pass. Browser assertions check finding counts and ordering as well as the existing end-to-end journey.

## Remaining analytical gaps and pilot readiness

- Ranking is category-based and heuristic, not a numerical measure of investment materiality. Table-only metrics and passages longer than the selection bound can be missed; nearby context can be incomplete. No inference is made that an omitted topic is immaterial.
- Kaspi's memo remains richer on Payments mix, deposit repricing, regulatory capital and parent distributable cash. The five-finding cap does not promote every later dividend event or the whole acquisition/IAS 29 bridge. Detailed official developments remain in the full report, but their prioritization is still imperfect.
- Annual calculations remain separate from interim evidence. Revenue/profit conversion, comparable scope, organic growth and causal contributions remain unresolved. A management quote is not independent corroboration. Interpretation checks do not establish semantic entailment.
- Kaspi independent news remains unavailable in the reviewed route: the feed worked, but no matching article was found. This is neither network failure nor evidence that no material news exists. Apple/Microsoft each have only one reviewed publisher/article, not comprehensive independent coverage.
- Reviewed annual extraction remains **Apple, Microsoft and Kaspi.kz only**. Source-text selection does not expand reviewed financial coverage.

**Ready for one small, supervised synthesis pilot, not autonomous investment conclusions.** A disabled Kaspi pilot packet is included in the artifact index. It contains selected recent passages/context, current findings, cited annual calculation inputs, coverage and warnings; it makes no news claims. The complete report/bundle also contains the broader news records. The pilot must use the existing provider, evidence-binding checks and cumulative spend ledger, require human review of every interpretation, and fail closed on unsupported claims.

No model call has been made and no spend is authorized here. The packet is under 64KiB with a 1,200-token output cap. Its accompanying estimate uses the existing conservative UTF-8-byte token allowance and **illustrative, unverified** $1/million input and $4/million output rates. These are a planning scenario, not a model quote. Before one proposed $0.10-capped Kaspi run, select a compatible model, verify its current rates, re-estimate and obtain explicit authorization. The next action is to review the linked Kaspi output and decide whether that narrow pilot is worth running.
