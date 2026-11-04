# Kinsella Revisited: A Longitudinal Replication

Code and data for the article *Kinsella Revisited: Concentration and
Diversification in the Post-Cold War Arms Trade Network, 2005-2025*
(accepted for publication, 2026), a replication and extension of David
Kinsella's (2003) social network analysis of the international arms trade
using SIPRI Arms Transfers Database data through 2025.

Every table and figure in the accepted version is reproduced by the
scripts in `src/`; the published figures are reproduced pixel for pixel.

## Research question

Kinsella (2003) argued that the arms trade is shaped by an interaction
between commercial and political logics, and expected that the end of
Cold War bipolarity would produce a more dispersed, less centralized
supplier structure over time. This project asks: two decades on, has
that marketization continued — or has supplier concentration persisted
or deepened?

## Key findings

- Out-degree centralization rose from **0.36 (2005) to 0.54 (2020)** and
  held at that level in 2025; the Herfindahl-Hirschman Index (HHI) rose
  from **0.18 to 0.21** over the same period. The supplier structure has
  become *more* concentrated, not less, contrary to Kinsella's
  expectation, although the deepening appears to have halted after 2020.
- The leading supplier's share of global transfer value rose from
  **31% to 42%**.
- This aggregate trend conceals a dual dynamic: **consolidation at the
  top** (Russia's out-degree centrality fell from 0.29 in 2010 to 0.09 in
  2025, leaving the top ten suppliers for the first time in the series)
  alongside **entry below it** (Türkiye enters the top ten by out-degree
  in 2025, with clients rising from 4 to 20; South Korea enters the top
  ten by transfer value in 2020).
- Robustness: excluding engine and sensor ties (6-10% of total TIV)
  lowers the levels but leaves the pattern unchanged — concentration
  rises to 2020 and then plateaus (Table 5). Recomputing over rolling
  five-year windows gives the same upward direction (Figure 2).
- Scope: the analysis measures the *concentration* dimension of
  Kinsella's marketization argument, not its relational dimension (the
  structural equivalence of suppliers' client bases).

## Data

Source: [SIPRI Arms Transfers Database](https://www.sipri.org/databases/armstransfers),
Trade Register export of deliveries 1995-2025, downloaded on 12 July 2026.
All figures reflect that extract; the database is updated annually.
Delivery-year records are used (not order dates), with SIPRI TIV
(trend-indicator value) as the transfer weight. The cross-sections cover
2005-2025; deliveries from 2004 are kept only for the first five-year
window of Figure 2 (2004-2008).

Entries SIPRI records as "unknown supplier(s)", "unknown recipient(s)",
non-state armed groups (names ending in `*`) and international
organizations (`**`) are kept as nodes, following SIPRI's own practice.
They account for 1.9-3.7% of ties and, except in 2020 (2.9%), less than
1% of total TIV (`output/tables/check_nonstate_share.csv`).

**Raw data is not redistributed in this repository** — SIPRI's terms
require users to query the database directly. To reproduce:

1. Go to the [SIPRI Trade Register](https://www.sipri.org/databases/armstransfers) query page
2. Set supplier/recipient to "All countries", delivery years 1995-2025
3. Export as CSV and place it at `data/raw/1995-2025.csv`

## Method summary

- Five annual cross-sections (2005, 2010, 2015, 2020, 2025), following
  Kinsella's approach of examining the network at several points in time.
- Directed, weighted edges: supplier → recipient, weight = summed TIV of
  deliveries in that year. Transfers of different weapon categories
  between the same pair are aggregated into one edge.
- Degree-based measures use only the existence of ties; transfer volume
  enters through the HHI.

The formulas are defined once, in `src/kinsella_measures.py`, and used by
every script. Equation numbers refer to the paper; equations 1-4 follow
Kinsella (2003, 18-20). *g* is the number of actors with at least one tie,
*L* the number of directed ties.

| Measure | Formula |
|---|---|
| Out-/in-degree (eq. 1) | number of distinct recipients / suppliers |
| Density (eq. 2) | (Σ out-degree + Σ in-degree) / g(g−1) = 2L / g(g−1) |
| Out-degree centrality (eq. 3) | out-degree / (g−1) |
| Group centralization (eq. 4) | Σ [max out-degree − out-degree] / (g−1)² |
| HHI (eq. 5) | Σ sᵢ², sᵢ = supplier i's share of total TIV |

Component-level ties are SIPRI's "Engines" and "Sensors" armament
categories, which SIPRI records separately when they originate from a
supplier other than the platform's.

## Outputs and the paper

| In the paper | File | Script |
|---|---|---|
| Table 1 | `output/tables/table1_density_centralization.csv` | `02_network_metrics.py` |
| Table 2 | `output/tables/table2_top20_outdegree.csv` | `02_network_metrics.py` |
| Table 3 | `output/tables/table3_hhi_marketshare.csv` | `02_network_metrics.py` |
| Table 4 | `output/tables/table4_top10_marketshare.csv` | `02_network_metrics.py` |
| Table 5 | `output/tables/table5_platform_only.csv` | `03_robustness_check.py` |
| Figures 1a-1e | `output/figures/figure_1a_2005.png` … `figure_1e_2025.png` | `06_figure1_network_maps.R` |
| Figure 2 | `output/figures/figure_2_moving_window.png` (data: `output/tables/figure2_moving_window.csv`) | `05_moving_window.py`, `07_figure2_moving_window.R` |
| Text: component share of TIV (6-10%) | `output/tables/check_component_share.csv` | `03_robustness_check.py` |
| Text: non-state and unknown entries | `output/tables/check_nonstate_share.csv` | `03_robustness_check.py` |
| Text: Russia's out-/in-degree balance and 2025 suppliers | `output/tables/check_russia_balance.csv`, `output/tables/check_russia_2025_suppliers.csv` | `04_discussion_checks.py` |

## Repository structure

```
├── data/
│   ├── raw/             # SIPRI export (not redistributed — see above)
│   └── processed/       # cleaned deliveries + cross-section edge lists
├── src/
│   ├── kinsella_measures.py        # shared formulas (equations 1-5)
│   ├── 01_clean_data.py            # load, clean, build cross-section edges
│   ├── 02_network_metrics.py       # Tables 1-4
│   ├── 03_robustness_check.py      # Table 5, component and non-state shares
│   ├── 04_discussion_checks.py     # Russia in/out-degree balance
│   ├── 05_moving_window.py         # Figure 2 data (five-year windows)
│   ├── 06_figure1_network_maps.R   # Figures 1a-1e
│   └── 07_figure2_moving_window.R  # Figure 2
├── notebooks/
│   └── pipeline.ipynb    # runs the Python steps, Colab-ready
├── output/
│   ├── tables/           # all output tables as CSV
│   └── figures/          # Figures 1a-1e and 2 as PNG
├── paper/
│   └── research_note.md  # early working draft (superseded, see below)
└── requirements.txt
```

`paper/research_note.md` is an early working draft kept for reference.
Its figures predate the corrections listed below; the accepted article
and the outputs in this repository supersede it.

## Reproducing the analysis

### Option A: notebook (recommended for inspecting the data)

Open [`notebooks/pipeline.ipynb`](notebooks/pipeline.ipynb) — either
locally in Jupyter, or on Google Colab via the "Open in Colab" badge at
the top of the notebook. It runs every Python step in order and displays
each resulting table inline, then shows the committed figures. Steps 2-5
work out of the box against the processed data already committed to this
repo; Step 1 (raw-data cleaning) only runs if you've supplied your own
SIPRI export (see [Data](#data) above).

### Option B: command line

```bash
pip install -r requirements.txt
cd src
python 01_clean_data.py
python 02_network_metrics.py
python 03_robustness_check.py
python 04_discussion_checks.py
python 05_moving_window.py
Rscript 06_figure1_network_maps.R
Rscript 07_figure2_moving_window.R
```

Each script reads the previous script's output from `data/processed/`
or `output/`, so they must be run in order on a first pass. The two R
scripts draw the published figures and need the R packages tidyverse,
igraph, ggraph and ggrepel (tested with R 4.5.3, igraph 2.3.3,
ggraph 2.2.2, ggrepel 0.9.8).

## Changes in this version (accepted article, November 2026)

Compared with the July 2026 version of this repository:

- **Density** now follows Kinsella's formula exactly, counting each
  directed tie once as an out-degree and once as an in-degree
  (2L / g(g−1)). Reported values therefore double (0.048-0.056, previously
  0.024-0.028).
- **Centralization** now uses Kinsella's denominator (g−1)² instead of
  g(g−1); values rise slightly (e.g. 2005: 0.3635, previously 0.3604).
- **Component-level ties** are now defined as Engines and Sensors only
  (previously also Naval weapons and Other), and the robustness check
  covers density, centralization and HHI (Table 5), not centralization
  alone.
- **New:** five-year moving-window measures (Figure 2) and the
  non-state/unknown entry check.
- **Figures 1a-1e** are now the published versions, drawn in R.
- Output files that were not paper tables are renamed with a `check_`
  prefix, so `tableN_` files match the paper's table numbers.

## Future work

- **Structural equivalence:** measuring the relational dimension of
  Kinsella's marketization argument — how far leading suppliers come to
  share an overlapping set of clients — for instance with the
  Euclidean-distance and multidimensional-scaling approach Kinsella
  (2003) applied to the sociomatrix.
- **Network resilience:** simulating the effect of removing top
  suppliers on overall connectivity and density, to assess whether the
  arms trade's current concentration is fragile or robust to a shock
  affecting a dominant supplier.
- **Testing Kinsella's bloc-dispersion mechanism directly:** coding
  states into Cold War-era alliance blocs and measuring intra- versus
  inter-bloc transfer shares over time, extending the analysis
  backward to pre-2005 cross-sections where data permits.

## Citation

Kinsella, D. (2003). *Changing structure of the arms trade: A social
network analysis.*
https://pdxscholar.library.pdx.edu/cgi/viewcontent.cgi?article=1018&context=polisci_fac

SIPRI. (n.d.). *Sources and methods: SIPRI Arms Transfers Database.*
https://www.sipri.org/databases/armstransfers/sources-and-methods

## License

Code: MIT. Data: subject to SIPRI's terms of use (not redistributed here).
