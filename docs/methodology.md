# Methodology and interpretation

Study: [Amendes de protection des données en Europe](https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html). Release: **2026.10.30.1**. Collection as of **25 October 2026**, with sources rechecked and corrections published on **30 October 2026**. Population reference: **1 January 2026**.

## Observation and selection

One row represents a documented decision or individually described enforcement case. A decision can include several fine components, findings or organizations, so a case count is not necessarily a fine count or an organization count.

The source collection retains up to 200 observations per country, ordered using the date actually available: decision date, publication date or reported year. `date_kind`, `publication_date`, `report_year`, `decision_year` and the country coverage notes preserve those distinctions. A publication date must not be re-labelled as a decision date. The collection is not certified to contain each country's latest 200 national decisions; `certified_latest_200` remains false.

The coverage includes GDPR, cookie rules and related national data-protection regimes. Do not label every record a GDPR-only fine. Keep `legal_regime`, `scope_classification`, legal references and source notes where present. The absence of those optional fields does not establish a particular legal basis.

Each country's coverage, authority coverage, periods, amount basis and limitations are retained in `data/dataset.json`, `data/country-summary.json` and the corresponding country extract. The public [25 October audit notes](../source/audit-2026-10-25.fr.md), [30 October audit record](../source/audit-2026-10-30.json) and [Greek screening journal](../source/greece-screening.json) describe documented exclusions, corrections and source limits. These records do not establish exhaustive national coverage.

## Amounts

- `amount_original` and `currency` preserve the recorded original money where available.
- `amount_eur` is the value retained by the published snapshot for its country calculation. It may reflect a documented reduction or another source-specific amount stage. It is not necessarily the original amount, a paid amount or a final judgment.
- Additional stage fields and `amount_status`, `amount_note`, `appeal_note` and source URLs must travel with the amount.
- Missing, withheld, inseparable, unallocated or non-convertible amounts stay null. An unallocated group amount must not be invented as an individual amount.
- A blank CSV value can also represent a field absent from that record. JSON preserves absence and explicit null separately.
- The release builder preserves the published `amount_eur` values. It checks their arithmetic; it does not independently adjudicate appeal status or re-estimate an unpublished amount.

For PLN, the recorded `fx_rate_pln_per_eur` and `fx_date` identify the daily ECB rate retained for the dated decision, or the last earlier available rate. A missing exact decision date does not authorize a publication-date substitute. The source is the [ECB daily PLN/EUR series](https://data.ecb.europa.eu/data/datasets/EXR/EXR.D.PLN.EUR.SP00.A). These conversions are indicative comparisons, not accounting exchange rates.

## Per-resident calculation

For each country:

1. Select records with a non-null `amount_eur`.
2. Sum the retained case-level EUR values, already rounded to cents, using decimal arithmetic.
3. Divide that sum by the population on 1 January 2026.
4. Report the known/unknown amount counts alongside the result.

Population is from [Eurostat, population on 1 January](https://ec.europa.eu/eurostat/databrowser/view/tps00001/default/table?lang=fr). `population_status` preserves the supplied status code. Do not substitute a different year's denominator without a new version and an explicit methodological change.

Selections cover different periods and source populations. Consequently, this figure does not measure an annual fine rate, the risk of enforcement, national enforcement severity or a payment made by residents. Its numerator is a selected documentary sum.

## Themes and source depth

Themes describe coded initial findings in the source collection, with evidence links and paraphrases where recorded. A case may have several themes. `source_level` reports the recorded source/review depth, whose vocabulary is not standardized across countries. Some countries also retain untranslated `source_topics` that have not been mapped to the common classification.

The `data/case-themes.csv` bridge is appropriate for counting distinct cases by theme. Do not join it to cases and then sum money: each additional theme would duplicate a case's amount. Country-level theme frequencies cannot be interpreted as comparable national offence rates. An empty theme list can mean unclassified findings rather than absence of a breach.

## Reproduction and versioning

`data/dataset.json` is a frozen, byte-identical copy of the public JSON checked on 30 October 2026. `provenance.json` records its SHA-256 and source commit. The builder generates the CSV/JSON extracts, source index, field dictionary, notebook outputs and platform handoffs entirely offline from that file.

This reproduces published tables and assets. It does not recrawl sources, reconstruct the earlier raw research inputs, provide a new comprehensive legal review or perform a live appeal survey. `source/input-manifest.json` retains the originating input hashes and paths as provenance, not as files bundled with this repository.

Correct a case using its ID and official supporting source, publish a new snapshot version, rebuild the exports and charts, update the citation/changelog, and preserve the prior release tag. Do not overwrite a published snapshot silently.
