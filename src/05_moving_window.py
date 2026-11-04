"""
05_moving_window.py

Data behind Figure 2: out-degree centralization and HHI recomputed over
rolling five-year windows, 2008-2025, as a check that the single-year
cross-section trend is not an artefact of single-year observation.

For each window end year t, all deliveries in t-4 ... t are pooled into one
network (one weighted edge per supplier-recipient pair, as in the
cross-sections) and the measures are computed on that pooled network with
the same formulas as Tables 1 and 3 (kinsella_measures.py). Windows are
labelled by their end year, so the first window (2008) covers 2004-2008.
SIPRI presents its own trend analysis in five-year periods.

Values are written unrounded: 07_figure2_moving_window.R plots them, and
full precision reproduces the published figure exactly.

Input:  data/processed/deliveries_clean.csv
Output: output/tables/figure2_moving_window.csv
"""

from pathlib import Path
import pandas as pd

import kinsella_measures as km

try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    # __file__ isn't defined when this code is pasted directly into a Jupyter cell.
    # In that case, use the current working directory (go up one level if we're in src/).
    PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'src' else Path.cwd()
DELIVERIES_PATH = PROJECT_ROOT / "data/processed/deliveries_clean.csv"
TABLES_DIR = PROJECT_ROOT / "output/tables"
WINDOW_YEARS = 5
FIRST_END_YEAR, LAST_END_YEAR = 2008, 2025


def moving_window_measures(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for end_year in range(FIRST_END_YEAR, LAST_END_YEAR + 1):
        start_year = end_year - WINDOW_YEARS + 1
        d = df[df["Delivery year"].between(start_year, end_year)]
        m = km.network_measures(km.aggregate_edges(d))
        rows.append({
            "window_start": start_year, "window_end": end_year,
            "density": m["density"],
            "centralization": m["centralization"],
            "hhi": m["hhi"],
            "n_nodes": m["n_nodes"], "n_edges": m["n_edges"],
        })
    return pd.DataFrame(rows)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DELIVERIES_PATH)

    figure2 = moving_window_measures(df)
    figure2.to_csv(TABLES_DIR / "figure2_moving_window.csv", index=False)

    print("Figure 2 data (five-year windows, labelled by end year):")
    print(figure2.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
