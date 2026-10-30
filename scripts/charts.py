#!/usr/bin/env python3
"""Render reusable figures from this frozen dataset. Requires matplotlib."""
import json
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/dataset.json').read_text(encoding='utf-8'))
NAMES = dict(FR='France', DE='Germany', ES='Spain', LT='Lithuania', PL='Poland',
             LV='Latvia', IT='Italy', EE='Estonia', LU='Luxembourg', GR='Greece')
SOURCE = 'https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html'
BLUE, INK, GREY = '#2563eb', '#172033', '#dce2ea'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK,
    'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.edgecolor': GREY, 'svg.fonttype': 'none', 'svg.hashsalt': 'legiscope-2026.10.30.1'})


def frame(title, subtitle, footnote):
    figure, axis = plt.subplots(figsize=(12, 8.2))
    figure.subplots_adjust(left=.19, right=.91, top=.80, bottom=.21)
    figure.text(.055, .945, 'LEGISCOPE  /  OPEN RESEARCH', color=BLUE, fontsize=10, weight='bold')
    figure.text(.055, .89, title, fontsize=22, weight='bold')
    figure.text(.055, .85, subtitle, fontsize=10.5)
    figure.text(.055, .105, footnote, fontsize=9, linespacing=1.65)
    figure.text(.055, .045, 'Source: Legiscope study · release 2026.10.30.1 · collection as of 25 October 2026',
                 fontsize=9, color=BLUE, url=SOURCE)
    axis.set_axisbelow(True)
    axis.grid(axis='x', color='#edf0f4')
    axis.tick_params(axis='y', length=0)
    return figure, axis


def save(figure, name):
    folder = ROOT / 'charts'
    folder.mkdir(exist_ok=True)
    svg = folder / f'{name}.svg'
    figure.savefig(svg, metadata={'Date': None, 'Creator': 'Legiscope'})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
    figure.savefig(folder / f'{name}.png', dpi=160, metadata={'Software': 'Legiscope'})
    plt.close(figure)


rows = sorted(DATA['recent'], key=lambda r: NAMES[r['country_code']])
names = [NAMES[r['country_code']] for r in rows]
figure, axis = frame('How much of the selected case money is known?',
    'Availability of retained EUR amounts in the documented selections',
    'Unequal periods, publication coverage and legal regimes. Unknown values are retained as null.\n'
    'A documented selection is not an exhaustive national register. Original contributions: CC BY 4.0.')
known = [r['amount_known_count'] for r in rows]
unknown = [r['amount_unknown_count'] for r in rows]
axis.barh(names, known, color=BLUE, height=.63, label='Known EUR amount')
axis.barh(names, unknown, left=known, color=GREY, height=.63, label='Unknown EUR amount')
for i, row in enumerate(rows):
    axis.text(row['decision_count'] + 3, i, f"{row['amount_known_count']}/{row['decision_count']}", va='center', fontsize=10)
axis.set_xlim(0, 233)
axis.invert_yaxis()
axis.set_xlabel('Selected decisions', labelpad=12)
axis.legend(frameon=False, ncol=2, loc='lower left', bbox_to_anchor=(0, 1.015), borderaxespad=0, fontsize=9)
save(figure, 'amount-coverage')

figure, axis = frame('Documented amounts per resident',
    'Known retained EUR amounts in selected cases / population on 1 January 2026',
    'Selections cover different periods and legal regimes. Missing amounts are excluded; coverage is shown at right.\n'
    'Not an annual rate, enforcement-severity ranking or amount paid by residents. Original contributions: CC BY 4.0.')
axis.barh(names, [r['eur_per_resident'] for r in rows], color=BLUE, height=.63)
maximum = max(r['eur_per_resident'] for r in rows)
axis.set_xlim(0, maximum * 1.37)
for i, row in enumerate(rows):
    axis.text(row['eur_per_resident'] + .12, i, f"€{row['eur_per_resident']:.2f}", va='center', fontsize=10)
    axis.text(maximum * 1.35, i, f"{row['amount_known_count']}/{row['decision_count']} known", va='center', ha='right', fontsize=9)
axis.invert_yaxis()
axis.set_xlabel('EUR per resident in the selected documentary corpus', labelpad=12)
save(figure, 'amounts-per-resident')

france = [r for r in DATA['cases'] if r['country_code'] == 'FR']
counts = Counter(theme for row in france for theme in sorted(set(row['themes'])))
labels = {t['id']: t['label'] for t in DATA['themes']}
top = counts.most_common(10)
figure, axis = frame('Les thèmes les plus cités dans la sélection française',
    f'{len(france)} décisions documentées · plusieurs thèmes possibles par dossier',
    'Constats initiaux codés dans les sources ; les recours connus restent signalés sur les dossiers.\n'
    'Ces fréquences ne se comparent pas entre pays. Contributions originales : CC BY 4.0.')
figure.subplots_adjust(left=.40)
axis.barh(['\n'.join(textwrap.wrap(labels[t], 42)) for t, _ in top], [n for _, n in top], color=BLUE, height=.63)
for i, (_, count) in enumerate(top):
    axis.text(count + 1, i, f'{count} / {len(france)}', va='center', fontsize=10)
axis.set_xlim(0, max(n for _, n in top) * 1.27)
axis.invert_yaxis()
axis.set_xlabel('Nombre de décisions mentionnant le thème', labelpad=12)
save(figure, 'france-themes')
print('Rendered 3 SVG and 3 PNG charts from data/dataset.json')
