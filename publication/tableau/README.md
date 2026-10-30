# Tableau Public data

`cases.csv` has one row per case. `case-themes.csv` is a many-row theme bridge; relate it logically by case ID. Use `COUNTD(id)` for decisions and never sum case money after physically joining it to the theme bridge. `country-summary.csv` already contains the reproduced country amounts and ratios with coverage notes.

Keep original currencies, unknown amounts and appeal/source information visible in case inspection. The countries have unequal periods and legal regimes; per-resident figures do not rank national enforcement severity. Theme classification depth varies between countries.

Build and review a native workbook, then publish it under the actual authorized Tableau Public account. These files are CSV inputs, not an already-verified Tableau workbook.

Study and source link: <https://www.legiscope.com/blog/amendes-rgpd-europe-comparaison-pays.html>

Exact release and scoped licences: <https://github.com/legiscope/gdpr-data-study/tree/v2026.10.30.1>
