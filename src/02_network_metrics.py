"""
02_network_metrics.py

Produces Tables 1-4 from the paper, starting from edges_cross_sections.csv:
  Table 1: density, centralization, node/edge counts (5 cross-sections)
  Table 2: top 20 suppliers by out-degree centrality (5 cross-sections)
  Table 3: HHI + leading supplier's market share (5 cross-sections)
  Table 4: top 10 suppliers by TIV share (5 cross-sections)

Formulas (Kinsella 2003, 18-20; paper equations 1-5) are defined once in
kinsella_measures.py:
  density        = 2L / g(g-1)
  centralization = sum(max(out-degree) - out-degree_i) / (g-1)^2
                   -- uses raw (unnormalized) out-degree
  out-degree centrality (normalized) = raw_out-degree / (g-1)
  HHI            = sum(share_i^2), share_i = supplier i's total TIV / network's total TIV

Input:  data/processed/edges_cross_sections.csv
Output: output/tables/table1_density_centralization.csv
        output/tables/table2_top20_outdegree.csv
        output/tables/table3_hhi_marketshare.csv
        output/tables/table4_top10_marketshare.csv
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
EDGES_PATH = PROJECT_ROOT / "data/processed/edges_cross_sections.csv"
TABLES_DIR = PROJECT_ROOT / "output/tables"
YEARS = [2005, 2010, 2015, 2020, 2025]


def compute_table1_and_2(edges: pd.DataFrame):
    table1_rows = []
    table2_rows = []

    for year in YEARS:
        G = km.build_graph(edges[edges["year"] == year])

        table1_rows.append({
            "year": year,
            "density": round(km.density(G), 4),
            "centralization": round(km.centralization(G), 4),
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
        })

        outdeg_norm = km.out_degree_centrality(G)
        top20 = sorted(outdeg_norm.items(), key=lambda x: -x[1])[:20]
        for rank, (supplier, score) in enumerate(top20, start=1):
            table2_rows.append({
                "year": year, "rank": rank, "supplier": supplier,
                "out_degree_centrality": round(score, 3),
            })

    return pd.DataFrame(table1_rows), pd.DataFrame(table2_rows)


def compute_table3_and_4(edges: pd.DataFrame):
    table3_rows = []
    table4_rows = []

    for year in YEARS:
        shares = km.supplier_shares(edges[edges["year"] == year])

        table3_rows.append({
            "year": year, "hhi": round((shares ** 2).sum(), 4),
            "top_supplier": shares.idxmax(), "top_market_share": round(shares.max(), 4),
        })

        top10 = shares.head(10)
        for rank, (supplier, share) in enumerate(top10.items(), start=1):
            table4_rows.append({
                "year": year, "rank": rank, "supplier": supplier,
                "market_share": round(share, 3),
            })

    return pd.DataFrame(table3_rows), pd.DataFrame(table4_rows)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    edges = pd.read_csv(EDGES_PATH)

    table1, table2 = compute_table1_and_2(edges)
    table3, table4 = compute_table3_and_4(edges)

    table1.to_csv(TABLES_DIR / "table1_density_centralization.csv", index=False)
    table2.to_csv(TABLES_DIR / "table2_top20_outdegree.csv", index=False)
    table3.to_csv(TABLES_DIR / "table3_hhi_marketshare.csv", index=False)
    table4.to_csv(TABLES_DIR / "table4_top10_marketshare.csv", index=False)

    print("Table 1 (density & centralization):")
    print(table1.to_string(index=False))
    print()
    print("Table 3 (HHI & top supplier):")
    print(table3.to_string(index=False))


if __name__ == "__main__":
    main()
