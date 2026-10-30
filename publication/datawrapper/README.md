# Datawrapper: two chart datasets

- `amounts-per-resident.csv`: selected documented EUR amounts divided by population on 1 January 2026, with known/unknown amount counts.
- `france-themes.csv`: cases tagged with each theme within the French selection; multiple themes per case.
- `chart-metadata.json`: title, source, byline and required coverage notes for the country chart.

Import a CSV, choose a suitable chart and inspect its rendering. Use the study URL in the source-link field and keep the coverage notes visible. The countries cover different periods and legal regimes; do not title the chart as national enforcement severity or a risk ranking. For the French theme chart, keep its own within-country denominator and multi-label explanation.

Set the source name and source URL in **Visualize → Annotate**, then publish and check the public link. Datawrapper documents that inserted links receive `nofollow noopener` attributes.

Official guide: <https://www.datawrapper.de/academy/how-to-insert-links>

Study: <https://www.legiscope.com/blog/europe-data-protection-fines-per-capita.html>

Reusable rendered figures and versioned source: <https://github.com/legiscope/gdpr-data-study/tree/v2026.10.30.2/charts>
