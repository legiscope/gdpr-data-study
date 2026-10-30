# Publish useful resources from this release

The [study](https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html) is the public explanation and citation destination. This repository supplies its versioned data and reproduction files. Use both links where helpful, and retain the amount-coverage and national-source notes.

## First publication batch

| Destination | Existing files | Account-side action |
|---|---|---|
| GitHub | Repository, citation, country extracts, charts and notebook | Publish this version on main with its immutable tag |
| [data.gouv.fr](data-gouv/README.md) | French CSV/JSON, theme frequencies and catalogue text | Select the real Legiscope organization, import the files and check the rendered source/method links |
| [Datawrapper](datawrapper/README.md) | Chart CSVs and source metadata | Import a CSV, configure the chart, retain coverage notes and the clickable study source, then publish |

After those resources are live, the same release can support these data routes:

| Destination | Existing files | Remaining work |
|---|---|---|
| [Kaggle](kaggle/README.md) | CSVs, frozen JSON, executed notebook and metadata template | Supply the actual Kaggle owner, import the dataset, attach it to the notebook and execute in the native runtime |
| [Hugging Face](hugging-face/README.md) | Dataset card, separate case/summary configurations, CSVs and JSON | Create a Dataset repository, upload the folder and inspect both native viewers |
| [Zenodo](zenodo/README.md) | Deposit metadata, citation and reproducible release | Use the real organization account, verify publication metadata, upload the release and publish; add the real DOI only after assignment |
| [Flourish](flourish/README.md) | Country amounts and French theme CSVs | Choose a template, bind the columns, retain source/coverage notes and review the published result |
| [Tableau Public](tableau/README.md) | Cases, theme bridge and country totals | Build logical relationships without duplicating money, review the workbook and publish |
| Observable | [Executed notebook](../notebooks/study.ipynb), [data](../data/) and [charts](../charts/) | Adapt the notebook to the native runtime and review the rendered output |

The prior 20-route distribution project also considered Postman, CodePen, DEV, Medium, YouTube, LinuxFr, Slashdot, Hacker News, Product Hunt, AFCDP and Next. This repository does not represent drafts, videos or imports for those routes as newly produced or published. Prior editorial assets need a fresh check against this snapshot before use.

## Source attribution

Suggested short source label: **Legiscope — European privacy fines study**.

Study URL: <https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html>

Exact release: <https://github.com/legiscope/gdpr-data-study/tree/v2026.10.30.1>

Attribution should identify version **2026.10.30.1**, collection as of **25 October 2026**, the relevant country scope, original CC BY 4.0 contributions and any modifications. The repository's scoped licensing does not relicense third-party sources.

## Check each actual placement

Record the live resource URL, cited study URL, publication date and observed link attributes. A prepared package or submitted form is not an acquired backlink. Journalists and associations decide whether and how to cite a resource. Platform source links can carry `nofollow`; assess the actual published link.

Outreach prospect identities and contact details are intentionally outside this public research repository. Publishing these assets does not send messages or establish any editorial acceptance.

## Make the local bundles

```bash
python3 scripts/build.py --package
```

This creates the complete release archive and seven platform archives in `dist/`. Native imports and publication remain separate. The release archive contains the frozen source dataset, methodology, provenance, citation, original licences and reproducible analysis.
