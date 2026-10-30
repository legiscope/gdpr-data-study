#!/usr/bin/env python3
"""Reproduce and verify exports of the frozen published study. Standard library only."""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import os
import zipfile
from collections import Counter
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
STUDY = 'https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html'
REPOSITORY = 'https://github.com/legiscope/gdpr-data-study'
NAMES = dict(FR='France', DE='Germany', ES='Spain', LT='Lithuania', PL='Poland',
             LV='Latvia', IT='Italy', EE='Estonia', LU='Luxembourg', GR='Greece')
DESCRIPTIONS = {
    'id': 'Stable case identifier in this collection.',
    'country_code': 'Two-letter country code; GR denotes Greece.',
    'authority': 'Authority or court identified in the source record.',
    'organisation': 'Organization or source-provided anonymized case description.',
    'date': 'Recorded date; interpret together with date_kind, not as an exact decision date by default.',
    'date_kind': 'Source-specific description of the date precision and meaning.',
    'date_note': 'Qualification of the recorded date.',
    'publication_date': 'Publication date when separately recorded.',
    'decision_year': 'Decision year when recorded without a complete date.',
    'report_year': 'Annual report year; not necessarily a decision year.',
    'decision_reference': 'Reference as recorded or normalized in the source collection.',
    'doc_web_id': 'Identifier of a document in an official web archive.',
    'amount_original': 'Original recorded amount in currency; may be null.',
    'currency': 'Currency of amount_original; EUR and PLN occur in this snapshot.',
    'amount_eur': 'Retained EUR amount used in this snapshot; null means no attributable convertible amount.',
    'amount_current_eur': 'Separately recorded current or revised EUR amount, if supplied.',
    'amount_current_pln': 'Separately recorded retained or revised PLN amount; explicit null does not restore the original amount.',
    'amount_exclusion_reason': 'Documented reason to exclude an amount from the retained EUR total.',
    'amount_gdpr_only_eur': 'Separately recorded GDPR-only EUR component when the source distinguishes regimes.',
    'amount_revised_pln': 'Separately recorded revised PLN amount, if supplied.',
    'amount_before_reduction_eur': 'Recorded EUR amount before a retained reduction.',
    'amount_status': 'Source-specific description of the amount stage or availability.',
    'amount_note': 'Qualification of amount, allocation or source coverage.',
    'amount_description': 'Additional description of the source monetary statement.',
    'amount_locator': 'Location of the monetary statement in the source.',
    'fine_count': 'Recorded number of fine components; do not substitute for the decision count.',
    'fine_components_eur': 'Separately recorded EUR fine components; not additional rows to add to amount_eur.',
    'fine_components_pln': 'Separately recorded PLN fine components; not additional rows to add to amount_eur.',
    'fx_date': 'Recorded ECB reference-rate date used for the indicative PLN conversion.',
    'fx_rate_pln_per_eur': 'Recorded number of PLN for one EUR at fx_date.',
    'source_url': 'Main cited source URL.',
    'decision_url': 'Direct decision document URL where recorded.',
    'source_level': 'Original source/review-depth label; vocabularies differ between countries.',
    'summary_fr': 'French-language authored summary retained from the published snapshot.',
    'themes': 'Zero or more common theme IDs; an empty array need not mean no findings.',
    'evidence': 'Recorded finding paraphrases and source references, with source-specific structure.',
    'source_topics': 'Original topic labels retained without claiming common-taxonomy mapping.',
    'unmapped_findings': 'Recorded findings not mapped to the common theme dictionary.',
    'appeal_note': 'Recorded appeal or payment qualification; not an exhaustive current appeal survey.',
    'appeal_source_urls': 'Source links retained for appeal or court outcomes.',
    'amount_revised_source_url': 'Source for the separately recorded revised amount.',
    'amount_source_url': 'Additional source for the monetary amount.',
    'date_source_url': 'Additional source for the recorded date.',
    'fx_source_url': 'ECB source for the indicative exchange rate.',
    'case_status_notice': 'Recorded warning about case status or subsequent developments.',
    'legal_regime': 'Legal-regime description where explicitly recorded.',
    'legal_basis_verified': 'Recorded verification flag; absence does not establish legal basis.',
    'legal_provisions': 'Legal provisions retained from the source collection.',
    'scope_classification': 'Recorded classification of the legal scope.',
    'scope_source_url': 'Source for the legal-scope classification.',
    'source_reference_as_printed': 'Reference exactly as printed in the underlying source.',
    'source_title_original': 'Original-language title of the cited source.',
    'register_status_original': 'Original status label in the source register at collection.',
    'register_status_fr': 'French rendering of the recorded register status.',
    'register_status_source_url': 'Source for the recorded register status.',
}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def csv_bytes(rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        result = {}
        for key in fields:
            value = row.get(key)
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
            elif isinstance(value, bool):
                value = str(value).lower()
            if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
                value = "'" + value
            result[key] = value
        writer.writerow(result)
    return ('\ufeff' + stream.getvalue()).encode('utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data, provenance):
    raw = (ROOT / 'data/dataset.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == provenance['snapshot_sha256'], 'Frozen snapshot hash differs')
    require(data['meta']['version'] == provenance['dataset_version'], 'Snapshot version differs')
    cases = data['cases']
    require(len(cases) == len({r['id'] for r in cases}) == provenance['case_count'], 'Case count or IDs differ')
    require(len(data['countries']) == len(data['recent']) == provenance['country_count'], 'Country count differs')
    require({r['country_code'] for r in data['recent']} == set(NAMES), 'Country set differs')
    known_themes = {r['id'] for r in data['themes']}
    for row in cases:
        require(row['country_code'] in NAMES, f"Unknown country: {row['id']}")
        require(row['source_url'].startswith('https://'), f"Missing source: {row['id']}")
        require(len(row['themes']) == len(set(row['themes'])) and set(row['themes']) <= known_themes,
                f"Invalid themes: {row['id']}")
        amount = row.get('amount_eur')
        require(amount is None or Decimal(str(amount)) >= 0, f"Invalid amount: {row['id']}")
    country_notes = {r['code']: r for r in data['countries']}
    for summary in data['recent']:
        code = summary['country_code']
        rows = [r for r in cases if r['country_code'] == code]
        known = [r for r in rows if r.get('amount_eur') is not None]
        require(len(rows) == summary['decision_count'] == country_notes[code]['case_count'], f'{code}: count differs')
        require(len(known) == summary['amount_known_count'], f'{code}: known amount count differs')
        require(len(rows) - len(known) == summary['amount_unknown_count'], f'{code}: unknown amount count differs')
        total = sum((Decimal(str(r['amount_eur'])) for r in known), Decimal('0')) if known else None
        require((total is None and summary['amount_eur'] is None) or total == Decimal(str(summary['amount_eur'])),
                f'{code}: country sum differs')
        require(summary['population'] > 0, f'{code}: population missing')
        if total is not None:
            ratio = total / Decimal(str(summary['population']))
            require(abs(ratio - Decimal(str(summary['eur_per_resident']))) < Decimal('0.000000000001'),
                    f'{code}: per-resident ratio differs')
        require(summary['certified_latest_200'] is False, f'{code}: unsupported latest-200 claim')


def source_index(data):
    sources = {}

    def visit(value, field, country, case_id):
        if isinstance(value, dict):
            for key, item in value.items():
                visit(item, key, country, case_id)
        elif isinstance(value, list):
            for item in value:
                visit(item, field, country, case_id)
        elif isinstance(value, str) and (field.endswith('_url') or field.endswith('_urls')):
            parsed = urlsplit(value)
            if parsed.scheme in ('http', 'https') and parsed.netloc and not any(c.isspace() for c in value):
                entry = sources.setdefault(value, {'countries': set(), 'cases': set(), 'fields': set()})
                entry['countries'].add(country)
                if case_id:
                    entry['cases'].add(case_id)
                entry['fields'].add(field)

    for row in data['cases']:
        visit(row, '', row['country_code'], row['id'])
    for row in data['recent']:
        visit(row, '', row['country_code'], None)
    return [dict(source_id='src-' + hashlib.sha256(url.encode()).hexdigest()[:16], url=url,
                 country_codes=sorted(entry['countries']), cited_case_count=len(entry['cases']),
                 fields=sorted(entry['fields'])) for url, entry in sorted(sources.items())]


def notebook(data):
    cells = []

    def markdown(text):
        cells.append(dict(cell_type='markdown', metadata={}, source=text.splitlines(keepends=True)))

    def code(text):
        cells.append(dict(cell_type='code', metadata={}, execution_count=None,
                          source=text.splitlines(keepends=True), outputs=[]))

    markdown('# European privacy fines: reproduce the published snapshot\n\n'
             f'[Study and source notes]({STUDY}). Original Legiscope contributions: CC BY 4.0; code: MIT.\n\n'
             'The collection has unequal periods, mixed legal regimes and unknown amounts. '
             'Its per-resident figures do not rank national enforcement severity. '
             'This notebook runs with the Python standard library and contains outputs from actual execution.')
    code("import csv, io, json\nfrom pathlib import Path\nfrom decimal import Decimal\n"
         "candidates = [p / 'data/dataset.json' for p in (Path.cwd(), *Path.cwd().parents)]\n"
         "candidates += [Path.cwd() / 'dataset.json']\n"
         "if Path('/kaggle/input').exists():\n"
         "    candidates += sorted(Path('/kaggle/input').rglob('dataset.json'))\n"
         "dataset_path = next((p for p in candidates if p.is_file()), None)\n"
         "if dataset_path is None:\n    raise FileNotFoundError('Extract the release or attach the dataset first.')\n"
         "data = json.loads(dataset_path.read_text(encoding='utf-8'))\n"
         "cases = data['cases']\n"
         "print('Dataset:', data['meta']['version'])\n"
         "print('Cases:', len(cases), '| Countries:', len(data['recent']))")
    markdown('## Country totals and monetary coverage\n\n'
             'Recompute from the case records with Decimal arithmetic. Missing EUR amounts are excluded from '
             'the sum and counted explicitly. The denominator is the recorded population on 1 January 2026.')
    code("summary_rows = []\n"
         "for country in data['recent']:\n"
         "    rows = [r for r in cases if r['country_code'] == country['country_code']]\n"
         "    known = [r for r in rows if r.get('amount_eur') is not None]\n"
         "    total = sum((Decimal(str(r['amount_eur'])) for r in known), Decimal('0')) if known else None\n"
         "    ratio = total / Decimal(str(country['population'])) if total is not None else None\n"
         "    if total is not None and total != Decimal(str(country['amount_eur'])):\n"
         "        raise ValueError('Published country total differs')\n"
         "    summary_rows.append(dict(country=country['country_code'], decisions=len(rows), known=len(known),\n"
         "                             unknown=len(rows)-len(known), documented_eur=str(total),\n"
         "                             population=country['population'],\n"
         "                             eur_per_resident=str(ratio.quantize(Decimal('0.000001'))) if ratio is not None else None))\n"
         "stream = io.StringIO()\nwriter = csv.DictWriter(stream, fieldnames=list(summary_rows[0]))\n"
         "writer.writeheader()\nwriter.writerows(summary_rows)\nprint(stream.getvalue().strip())")
    markdown('## Findings in the French selection\n\n'
             'Count distinct cases per theme within France. One case may have several themes. '
             'These frequencies cannot be compared as national offence rates. '
             'Never sum money after joining the multi-theme bridge.')
    code("from collections import Counter\n"
         "france = [r for r in cases if r['country_code'] == 'FR']\n"
         "counts = Counter(theme for row in france for theme in sorted(set(row['themes'])))\n"
         "labels = {t['id']: t['label'] for t in data['themes']}\n"
         "for theme, count in counts.most_common(10):\n"
         "    print(f'{count:3} / {len(france)}  {labels[theme]}')")
    markdown('## Trace one observation to its source\n\n'
             'Original amounts, retained EUR values, appeal notes and source depth are distinct fields. '
             'Source links allow further review; their presence does not certify finality or complete reasoning review.')
    code("example = cases[0]\n"
         "for key in ['id', 'country_code', 'organisation', 'date', 'date_kind', 'amount_original',\n"
         "            'currency', 'amount_eur', 'source_level', 'appeal_note', 'source_url', 'decision_url']:\n"
         "    print(f'{key}: {example.get(key)}')")
    markdown(f'## Reuse\n\nCite [Legiscope and the study]({STUDY}), identify this frozen release and '
             'retain the coverage and source notes. See `docs/methodology.md` and `LICENSING.md` in the repository.')
    namespace = {'__name__': '__main__'}
    previous = Path.cwd()
    try:
        os.chdir(ROOT)
        count = 0
        for cell in cells:
            if cell['cell_type'] == 'code':
                count += 1
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec(compile(''.join(cell['source']), f'notebook-cell-{count}', 'exec'), namespace)
                cell['execution_count'] = count
                cell['outputs'] = [dict(output_type='stream', name='stdout', text=output.getvalue().splitlines(keepends=True))]
    finally:
        os.chdir(previous)
    return dict(nbformat=4, nbformat_minor=5, metadata=dict(
        kernelspec=dict(display_name='Python 3', language='python', name='python3'),
        language_info=dict(name='python', version='3.9')),
        cells=[dict(id=f'cell-{i+1}', **cell) for i, cell in enumerate(cells)])


def outputs(data, provenance):
    result = {}

    def table(path, rows):
        result[path + '.json'] = json_bytes(rows)
        result[path + '.csv'] = csv_bytes(rows)

    cases = data['cases']
    table('data/cases', cases)
    table('data/country-summary', data['recent'])
    table('data/themes', data['themes'])
    bridge = [dict(case_id=r['id'], country_code=r['country_code'], theme_id=theme)
              for r in cases for theme in r['themes']]
    table('data/case-themes', bridge)
    table('data/sources', source_index(data))
    coverage = []
    for country in data['countries']:
        code = country['code']
        rows = [r for r in cases if r['country_code'] == code]
        for level in sorted({r['source_level'] for r in rows}):
            selected = [r for r in rows if r['source_level'] == level]
            known = sum(r.get('amount_eur') is not None for r in selected)
            coverage.append(dict(country_code=code, source_level=level, case_count=len(selected),
                                 known_amount_count=known, unknown_amount_count=len(selected)-known))
        subset = dict(meta=dict(data['meta'], case_count=len(rows), country_count=1),
                      recent=[r for r in data['recent'] if r['country_code'] == code],
                      countries=[country], themes=data['themes'], cases=rows)
        result[f'data/countries/{code}.json'] = json_bytes(subset)
        result[f'data/countries/{code}.csv'] = csv_bytes(rows)
    table('data/source-coverage', coverage)
    fields = list(dict.fromkeys(k for r in cases for k in r))
    require(set(fields) <= set(DESCRIPTIONS), 'Add a description for each observed case field')
    dictionary = [dict(field=key,
                       types=sorted({type(r[key]).__name__ for r in cases if key in r and r[key] is not None}),
                       absent_count=sum(key not in r for r in cases),
                       null_count=sum(key in r and r[key] is None for r in cases), description=DESCRIPTIONS[key])
                  for key in fields]
    table('data/data-dictionary', dictionary)
    lines = ['# Case data dictionary', '', 'Generated from the frozen records. Optional fields retain their source meaning.', '',
             'CSV arrays/objects are JSON strings. Blank CSV cells represent null or absence; JSON preserves the distinction.', '',
             '| Field | Observed types | Absent | Null | Meaning |', '|---|---|---:|---:|---|']
    lines += [f"| `{r['field']}` | {', '.join(r['types'])} | {r['absent_count']} | {r['null_count']} | {r['description']} |"
              for r in dictionary]
    lines += ['', '## Country summaries', '',
              '`decision_count` counts selected decisions. `amount_known_count` and `amount_unknown_count` describe EUR availability. '
              '`amount_eur` is the decimal sum of retained case amounts and `eur_per_resident` divides that sum by `population`. '
              '`population_status`, country coverage, authority coverage, periods, amount notes and limitations remain attached. '
              '`certified_latest_200` is false for every country.', '',
              'See [methodology.md](methodology.md) for selection, currency and interpretation rules.', '']
    result['docs/data-dictionary.md'] = '\n'.join(lines).encode()
    executed = notebook(data)
    result['notebooks/study.ipynb'] = json_bytes(executed)

    version = provenance['release_version']
    tag = provenance['release_tag']
    raw = f'https://raw.githubusercontent.com/legiscope/gdpr-data-study/{tag}'
    fr = [r for r in cases if r['country_code'] == 'FR']
    theme_counts = Counter(t for r in fr for t in sorted(set(r['themes'])))
    labels = {t['id']: t['label'] for t in data['themes']}
    fr_themes = [dict(theme_id=t, theme=labels[t], cases=n, selected_cases=len(fr))
                 for t, n in theme_counts.most_common()]
    chart_rows = [dict(country_code=r['country_code'], country=NAMES[r['country_code']],
                       eur_per_resident=r['eur_per_resident'], selected_cases=r['decision_count'],
                       known_amount_cases=r['amount_known_count'], unknown_amount_cases=r['amount_unknown_count'],
                       population=r['population'], population_date=data['meta']['recent_population_date'])
                  for r in data['recent']]
    result['publication/datawrapper/amounts-per-resident.csv'] = csv_bytes(chart_rows)
    result['publication/datawrapper/france-themes.csv'] = csv_bytes(fr_themes)
    result['publication/datawrapper/chart-metadata.json'] = json_bytes(dict(
        title='Documented privacy-fine amounts per resident',
        description='Selected published decisions; unequal periods, coverage and legal regimes.',
        source_name='Legiscope — documented European privacy decisions', source_url=STUDY,
        byline='Legiscope', release_version=version,
        notes='Population on 1 January 2026. Known EUR amounts only. Not an annual rate or a ranking of enforcement severity. Retain known/unknown case counts.',
        native_status='CSV and metadata prepared; chart must be imported, reviewed and published in the platform.'))
    result['publication/flourish/amounts-per-resident.csv'] = csv_bytes(chart_rows)
    result['publication/flourish/france-themes.csv'] = csv_bytes(fr_themes)
    result['publication/tableau/cases.csv'] = result['data/cases.csv']
    result['publication/tableau/case-themes.csv'] = result['data/case-themes.csv']
    result['publication/tableau/country-summary.csv'] = result['data/country-summary.csv']
    result['publication/data-gouv/fr-cases.csv'] = result['data/countries/FR.csv']
    result['publication/data-gouv/fr-data.json'] = result['data/countries/FR.json']
    result['publication/data-gouv/fr-themes.csv'] = csv_bytes(fr_themes)
    description = (f'{len(fr)} décisions françaises de protection des données documentées dans la collecte Legiscope. '
                   'Les régimes RGPD, cookies et règles nationales liées peuvent être inclus. Montants, sources, '
                   'motifs et notes de recours conservés. Il ne s’agit pas d’un recensement national exhaustif. '
                   f'Étude et méthode : {STUDY} ; version {version}. Contributions originales CC BY 4.0 ; '
                   'les documents sources conservent leurs propres droits.')
    result['publication/data-gouv/metadata.json'] = json_bytes(dict(
        title=f'Sanctions de protection des données : {len(fr)} décisions françaises documentées',
        description=description, license='cc-by', frequency='unknown',
        tags=['cnil', 'rgpd', 'protection-des-donnees', 'sanctions'],
        resources=[dict(title='Décisions françaises CSV', file='fr-cases.csv', format='csv',
                        url=f'{raw}/publication/data-gouv/fr-cases.csv'),
                   dict(title='Données et notes de couverture JSON', file='fr-data.json', format='json',
                        url=f'{raw}/publication/data-gouv/fr-data.json'),
                   dict(title='Thèmes documentés', file='fr-themes.csv', format='csv',
                        url=f'{raw}/publication/data-gouv/fr-themes.csv')],
        account_step='Choose the actual Legiscope organisation in the platform; no organisation identifier is invented here.',
        payload_status='Editor handoff; not a submitted API payload.'))
    for destination in ['kaggle', 'hugging-face']:
        for name in ['cases.csv', 'country-summary.csv', 'themes.csv', 'sources.csv']:
            result[f'publication/{destination}/{name}'] = result[f'data/{name}']
        result[f'publication/{destination}/dataset.json'] = (ROOT / 'data/dataset.json').read_bytes()
        result[f'publication/{destination}/LICENSING.md'] = (ROOT / 'LICENSING.md').read_bytes()
        result[f'publication/{destination}/LICENSE-DATA'] = (ROOT / 'LICENSE-DATA').read_bytes()
        result[f'publication/{destination}/LICENSE'] = (ROOT / 'LICENSE').read_bytes()
        result[f'publication/{destination}/CITATION.cff'] = (ROOT / 'CITATION.cff').read_bytes()
    result['publication/kaggle/study.ipynb'] = json_bytes(executed)
    result['publication/kaggle/dataset-metadata.template.json'] = json_bytes(dict(
        title='European privacy fines: documented decisions and sources',
        id='REPLACE_KAGGLE_OWNER/european-privacy-fines', licenses=[dict(name='CC-BY-4.0')],
        subtitle='Selected cases across ten countries with sources and monetary coverage',
        description=f'{len(cases)} selected documented decisions; collection as of {data["meta"]["data_as_of"]}. '
                    f'Unequal periods and mixed legal regimes; not a national census or risk ranking. Study: {STUDY}. '
                    'CC BY 4.0 covers original contributions only; retain LICENSING.md and source rights.'))
    result['publication/hugging-face/README.md'] = (f'''---
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

By [Legiscope]({STUDY}). Release **{version}**, collection as of **{data['meta']['data_as_of']}**.

{len(cases):,} documented decisions across ten countries. Up to 200 selected decisions per country, with unequal periods, publication coverage and source depth. GDPR, cookie and related national regimes can be included. This is not a national census, enforcement-risk model or harmonized ranking.

`cases` contains case records. `country_summary` is a separate configuration, never extra case rows. The `train` name is a Hub split convention; the release supplies no training labels or benchmark claim. Nested case fields are JSON strings in CSV; `dataset.json` preserves native objects and nulls. Summary text and source notes are primarily French. Empty theme lists can represent unclassified findings.

Known and unknown EUR amounts are distinguished. Original currencies, recorded reductions, appeal notes and source URLs travel with the cases. Population is from 1 January 2026. Per-resident amounts are sums of selected known amounts divided by that population, not annual rates or amounts paid by residents.

Original selection, annotations, summaries and derived tables: **CC BY 4.0**. Third-party documents and source data retain their own terms. See LICENSING.md and LICENSE-DATA. Cite [the study]({STUDY}) and [this exact version]({REPOSITORY}/tree/{tag}); state modifications and retain source and coverage notes.

Methodology, reproducible code and notebook: [{REPOSITORY}]({REPOSITORY}). Full regulator documents are not bundled. No new exhaustive appeal review is claimed.
''').encode()
    zenodo = dict(title='European privacy fines: documented decisions and amounts per resident',
                  upload_type='dataset', creators=[dict(name='Legiscope')], version=version,
                  publication_date='2026-10-30', access_right='open', license='cc-by-4.0',
                  description=f'Frozen collection of {len(cases)} documented decisions across ten countries. '
                              f'Collection as of {data["meta"]["data_as_of"]}; population on 1 January 2026. '
                              'Unequal periods, mixed legal regimes, missing amounts and recorded appeal stages retained. '
                              f'Not a national census or enforcement-risk ranking. Study: {STUDY}. '
                              'CC BY 4.0 covers original Legiscope data/documentation; utility code is MIT and third-party source rights remain reserved.',
                  keywords=['privacy', 'GDPR', 'enforcement', 'open data'],
                  related_identifiers=[dict(identifier=STUDY, relation='isSupplementTo', scheme='url')])
    result['.zenodo.json'] = json_bytes(zenodo)
    result['publication/zenodo/metadata.json'] = json_bytes(dict(metadata=zenodo))
    return result


def release_paths():
    files = [ROOT / name for name in ['README.md', 'LICENSE', 'LICENSE-DATA', 'LICENSING.md', 'CITATION.cff',
                                     'CHANGELOG.md', 'provenance.json', 'requirements-charts.txt', '.zenodo.json']]
    for directory in ['data', 'source', 'scripts', 'charts', 'notebooks', 'publication', 'docs']:
        files += [p for p in (ROOT / directory).rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and 'superpowers' not in p.parts and p.suffix != '.pyc']
    return sorted(set(files))


def manifest():
    return dict(algorithm='sha256', files=[dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in release_paths()])


def package(provenance):
    folder = ROOT / 'dist'
    folder.mkdir(exist_ok=True)

    def archive(path, members):
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as stream:
            for name, file in sorted(members.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 30, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                stream.writestr(info, file.read_bytes())

    version = provenance['release_version']
    complete = {str(p.relative_to(ROOT)): p for p in [*release_paths(), ROOT / 'checksums.json']}
    archive(folder / f'gdpr-data-study-{version}.zip', complete)
    for name in ['data-gouv', 'datawrapper', 'kaggle', 'hugging-face', 'zenodo', 'flourish', 'tableau']:
        directory = ROOT / 'publication' / name
        members = {str(p.relative_to(directory)): p for p in directory.rglob('*') if p.is_file()}
        for filename in ['LICENSING.md', 'LICENSE-DATA', 'LICENSE', 'CITATION.cff']:
            members.setdefault(filename, ROOT / filename)
        if name == 'zenodo':
            members = complete
        archive(folder / f'{name}-{version}.zip', members)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify real data, exports and checksums without writing files')
    parser.add_argument('--package', action='store_true', help='Build verified local release ZIPs under dist/')
    args = parser.parse_args()
    require(not (args.check and args.package), 'Choose --check or --package')
    data = json.loads((ROOT / 'data/dataset.json').read_text(encoding='utf-8'))
    provenance = json.loads((ROOT / 'provenance.json').read_text(encoding='utf-8'))
    validate(data, provenance)
    generated = outputs(data, provenance)
    for relative, content in generated.items():
        path = ROOT / relative
        if args.check:
            require(path.is_file() and path.read_bytes() == content, f'Export differs: {relative}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    check_path = ROOT / 'checksums.json'
    if args.check:
        require(json.loads(check_path.read_text(encoding='utf-8')) == manifest(), 'Release checksum manifest differs')
    else:
        check_path.write_bytes(json_bytes(manifest()))
    if args.package:
        package(provenance)
    print(json.dumps(dict(status='pass', version=provenance['release_version'], cases=len(data['cases']),
        countries=len(data['recent']), unknown_amount_cases=sum(r.get('amount_eur') is None for r in data['cases']),
        generated_files=len(generated), source_urls=len(source_index(data)), notebook_code_cells=4,
        snapshot_sha256=provenance['snapshot_sha256'], mode='check' if args.check else 'build',
        packages_created=args.package), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, FileNotFoundError) as error:
        raise SystemExit(str(error))
