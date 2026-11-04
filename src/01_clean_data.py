"""
01_clean_data.py

Reads the raw SIPRI Arms Transfers Database export (Trade Register CSV),
cleans it, and prepares it for analysis.

Input:  data/raw/1995-2025.csv
Output: data/processed/deliveries_clean.csv       (2004-2025, all rows)
        data/processed/edges_cross_sections.csv   (supplier-recipient-TIV for the 5 cross-sections)

Notes on SIPRI's export format:
- The first 11 rows are metadata/description text (not the table) -> skipped with skiprows=11
- Line endings are Windows-style (\\r\\n) -- pandas handles this automatically
- The last column name has a stray trailing ";" character -> renamed
- "Delivery year" and "TIV delivery values" already come split out per row
  (allocated by year); no further computation/splitting is needed
"""

from pathlib import Path
import pandas as pd

# Locates the project root from the script's own location, so paths stay
# correct whether run from the terminal, from Jupyter, or from another directory.
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    # __file__ isn't defined when this code is pasted directly into a Jupyter cell.
    # In that case, use the current working directory (go up one level if we're in src/).
    PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'src' else Path.cwd()

RAW_PATH = PROJECT_ROOT / "data/raw/1995-2025.csv"
PROCESSED_DIR = PROJECT_ROOT / "data/processed"
CROSS_SECTION_YEARS = [2005, 2010, 2015, 2020, 2025]
# Cross-sections start in 2005; 2004 is kept only because the first five-year
# window behind Figure 2 (05_moving_window.py) runs 2004-2008.
MIN_DELIVERY_YEAR = 2004


def load_raw(path: str) -> pd.DataFrame:
    """Reads SIPRI's raw export starting from the correct row and cleans up
    the column-name artifact (stray ';' on the last column)."""
    df = pd.read_csv(path, skiprows=11, encoding="utf-8")
    df = df.rename(columns={"Local production;": "Local production"})
    return df


def filter_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Keeps only deliveries from 2004 onward (see MIN_DELIVERY_YEAR)."""
    return df[df["Delivery year"] >= MIN_DELIVERY_YEAR].copy()


def build_edges_for_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Computes the total TIV value per supplier-recipient pair for a given
    delivery year and produces a directed edge list."""
    d = df[df["Delivery year"] == year]
    edges = (
        d.groupby(["Supplier", "Recipient"])["TIV delivery values"]
        .sum()
        .reset_index()
        .rename(columns={
            "Supplier": "supplier",
            "Recipient": "recipient",
            "TIV delivery values": "tiv",
        })
    )
    edges.insert(0, "year", year)
    return edges


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_raw = load_raw(RAW_PATH)
    df_scoped = filter_scope(df_raw)

    # Full clean dataset (2004-2025), also used by the later robustness/discussion
    # scripts (the Armament category column is still present here)
    df_scoped.to_csv(PROCESSED_DIR / "deliveries_clean.csv", index=False)

    # Combine all five cross-sections into a single tidy-format file
    all_edges = pd.concat(
        [build_edges_for_year(df_scoped, y) for y in CROSS_SECTION_YEARS],
        ignore_index=True,
    )
    all_edges.to_csv(PROCESSED_DIR / "edges_cross_sections.csv", index=False)

    print(f"deliveries_clean.csv: {len(df_scoped)} rows (2004-2025)")
    print(f"edges_cross_sections.csv: {len(all_edges)} edges (total across 5 cross-sections)")
    for y in CROSS_SECTION_YEARS:
        n = all_edges[all_edges["year"] == y]
        nodes = set(n["supplier"]) | set(n["recipient"])
        print(f"  {y}: {len(nodes)} nodes, {len(n)} edges")


if __name__ == "__main__":
    main()
