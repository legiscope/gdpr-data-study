# Kaggle dataset and notebook handoff

1. Copy `dataset-metadata.template.json` to `dataset-metadata.json`.
2. Replace `REPLACE_KAGGLE_OWNER` with the actual authorized Kaggle account or organization. The GitHub organization is not assumed to be a Kaggle owner.
3. Create the dataset with the included CSV/JSON, citation and licensing files. Keep original contribution and third-party rights distinctions in the description.
4. Upload `study.ipynb` as a separate notebook, attach this dataset and run all cells in Kaggle. Its loader finds the frozen `dataset.json` under `/kaggle/input`.
5. Inspect the dataset and executed notebook before making them public. Retain the study link and exact version.

The case table and country-summary table are different statistical units. Do not concatenate them. Nested case fields are JSON-encoded CSV strings; `dataset.json` retains their native structure. Missing EUR amounts are not zero.

Metadata reference: <https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets_metadata.md>

Study: <https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html>

Release: <https://github.com/legiscope/gdpr-data-study/tree/v2026.10.30.1>
