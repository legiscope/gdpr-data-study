# Case data dictionary

Generated from the frozen records. Optional fields retain their source meaning.

CSV arrays/objects are JSON strings. Blank CSV cells represent null or absence; JSON preserves the distinction.

| Field | Observed types | Absent | Null | Meaning |
|---|---|---:|---:|---|
| `id` | str | 0 | 0 | Stable case identifier in this collection. |
| `country_code` | str | 0 | 0 | Two-letter country code; GR denotes Greece. |
| `authority` | str | 0 | 0 | Authority or court identified in the source record. |
| `date` | str | 0 | 114 | Recorded date; interpret together with date_kind, not as an exact decision date by default. |
| `date_kind` | str | 0 | 11 | Source-specific description of the date precision and meaning. |
| `organisation` | str | 0 | 135 | Organization or source-provided anonymized case description. |
| `decision_reference` | str | 0 | 323 | Reference as recorded or normalized in the source collection. |
| `amount_original` | float, int | 0 | 69 | Original recorded amount in currency; may be null. |
| `currency` | str | 0 | 0 | Currency of amount_original; EUR and PLN occur in this snapshot. |
| `amount_status` | str | 281 | 0 | Source-specific description of the amount stage or availability. |
| `source_url` | str | 0 | 0 | Main cited source URL. |
| `decision_url` | str | 542 | 165 | Direct decision document URL where recorded. |
| `source_level` | str | 0 | 0 | Original source/review-depth label; vocabularies differ between countries. |
| `summary_fr` | str | 0 | 0 | French-language authored summary retained from the published snapshot. |
| `themes` | list | 0 | 0 | Zero or more common theme IDs; an empty array need not mean no findings. |
| `evidence` | list | 0 | 0 | Recorded finding paraphrases and source references, with source-specific structure. |
| `appeal_note` | str | 267 | 30 | Recorded appeal or payment qualification; not an exhaustive current appeal survey. |
| `fine_count` | int | 0 | 174 | Recorded number of fine components; do not substitute for the decision count. |
| `amount_eur` | float | 0 | 77 | Retained EUR amount used in this snapshot; null means no attributable convertible amount. |
| `amount_source_url` | str | 536 | 0 | Additional source for the monetary amount. |
| `scope_classification` | str | 865 | 0 | Recorded classification of the legal scope. |
| `legal_basis_verified` | bool | 810 | 0 | Recorded verification flag; absence does not establish legal basis. |
| `scope_source_url` | str | 1012 | 0 | Source for the legal-scope classification. |
| `legal_provisions` | list | 604 | 0 | Legal provisions retained from the source collection. |
| `amount_current_eur` | int | 1031 | 2 | Separately recorded current or revised EUR amount, if supplied. |
| `amount_before_reduction_eur` | float, int | 902 | 0 | Recorded EUR amount before a retained reduction. |
| `appeal_source_urls` | list | 1018 | 0 | Source links retained for appeal or court outcomes. |
| `publication_date` | str | 734 | 17 | Publication date when separately recorded. |
| `date_note` | str | 914 | 0 | Qualification of the recorded date. |
| `amount_description` | str | 996 | 0 | Additional description of the source monetary statement. |
| `amount_note` | str | 856 | 0 | Qualification of amount, allocation or source coverage. |
| `case_status_notice` | str | 621 | 0 | Recorded warning about case status or subsequent developments. |
| `legal_regime` | str | 467 | 0 | Legal-regime description where explicitly recorded. |
| `report_year` | int | 942 | 0 | Annual report year; not necessarily a decision year. |
| `decision_year` | int | 918 | 0 | Decision year when recorded without a complete date. |
| `date_source_url` | str | 763 | 0 | Additional source for the recorded date. |
| `fine_components_eur` | list | 894 | 0 | Separately recorded EUR fine components; not additional rows to add to amount_eur. |
| `amount_locator` | str | 415 | 0 | Location of the monetary statement in the source. |
| `amount_exclusion_reason` | str | 1035 | 0 | Documented reason to exclude an amount from the retained EUR total. |
| `unmapped_findings` | list | 1041 | 0 | Recorded findings not mapped to the common theme dictionary. |
| `register_status_original` | str | 909 | 0 | Original status label in the source register at collection. |
| `register_status_fr` | str | 909 | 0 | French rendering of the recorded register status. |
| `register_status_source_url` | str | 909 | 0 | Source for the recorded register status. |
| `fine_components_pln` | list | 901 | 0 | Separately recorded PLN fine components; not additional rows to add to amount_eur. |
| `fx_date` | str | 907 | 0 | Recorded ECB reference-rate date used for the indicative PLN conversion. |
| `fx_rate_pln_per_eur` | float | 907 | 0 | Recorded number of PLN for one EUR at fx_date. |
| `fx_source_url` | str | 907 | 0 | ECB source for the indicative exchange rate. |
| `amount_current_pln` | int | 1036 | 5 | Separately recorded retained or revised PLN amount; explicit null does not restore the original amount. |
| `amount_revised_pln` | int | 1040 | 0 | Separately recorded revised PLN amount, if supplied. |
| `amount_revised_source_url` | str | 1040 | 0 | Source for the separately recorded revised amount. |
| `source_topics` | list | 722 | 0 | Original topic labels retained without claiming common-taxonomy mapping. |
| `doc_web_id` | str | 842 | 0 | Identifier of a document in an official web archive. |
| `source_reference_as_printed` | str | 1039 | 0 | Reference exactly as printed in the underlying source. |
| `amount_gdpr_only_eur` | int | 912 | 10 | Separately recorded GDPR-only EUR component when the source distinguishes regimes. |
| `source_title_original` | str | 912 | 1 | Original-language title of the cited source. |

## Country summaries

`decision_count` counts selected decisions. `amount_known_count` and `amount_unknown_count` describe EUR availability. `amount_eur` is the decimal sum of retained case amounts and `eur_per_resident` divides that sum by `population`. `population_status`, country coverage, authority coverage, periods, amount notes and limitations remain attached. `certified_latest_200` is false for every country.

See [methodology.md](methodology.md) for selection, currency and interpretation rules.
