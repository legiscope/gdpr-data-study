---
pretty_name: European privacy fines — documented decisions
language:
- fr
- en
license: cc-by-4.0
tags:
- privacy
- gdpr
- legal
- open-data
configs:
- config_name: cases
  data_files:
  - split: train
    path: cases.csv
- config_name: country_summary
  data_files:
  - split: train
    path: country-summary.csv
---
# European privacy fines: documented decisions

By [Legiscope](https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html). Release **2026.10.30.1**, collection as of **2026-10-25**.

1,042 documented decisions across ten countries. Up to 200 selected decisions per country, with unequal periods, publication coverage and source depth. GDPR, cookie and related national regimes can be included. This is not a national census, enforcement-risk model or harmonized ranking.

`cases` contains case records. `country_summary` is a separate configuration, never extra case rows. The `train` name is a Hub split convention; the release supplies no training labels or benchmark claim. Nested case fields are JSON strings in CSV; `dataset.json` preserves native objects and nulls. Summary text and source notes are primarily French. Empty theme lists can represent unclassified findings.

Known and unknown EUR amounts are distinguished. Original currencies, recorded reductions, appeal notes and source URLs travel with the cases. Population is from 1 January 2026. Per-resident amounts are sums of selected known amounts divided by that population, not annual rates or amounts paid by residents.

Original selection, annotations, summaries and derived tables: **CC BY 4.0**. Third-party documents and source data retain their own terms. See LICENSING.md and LICENSE-DATA. Cite [the study](https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html) and [this exact version](https://github.com/legiscope/gdpr-data-study/tree/v2026.10.30.1); state modifications and retain source and coverage notes.

Methodology, reproducible code and notebook: [https://github.com/legiscope/gdpr-data-study](https://github.com/legiscope/gdpr-data-study). Full regulator documents are not bundled. No new exhaustive appeal review is claimed.
