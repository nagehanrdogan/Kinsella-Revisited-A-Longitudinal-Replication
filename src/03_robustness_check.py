"""
03_robustness_check.py

Produces Table 5 and the two scope checks reported in the paper's text:
  Table 5:         density, centralization and HHI with and without
                   component-level ties ("Full" vs. "Platform-only"),
                   5 cross-sections.
  Component share: component-level transfers as a share of total TIV
                   (the "6 to 10 per cent" in the Results and Limitations).
  Non-state share: share of ties and TIV involving unknown suppliers or
                   recipients, non-state armed groups and international
                   organizations (the "1.9 to 3.7 per cent of ties" in the
                   Method section).

Component-level ties are SIPRI's "Engines" and "Sensors" armament
categories: the sub-system categories SIPRI records as separate rows when
they originate from a supplier other than the platform's. Every other
category is treated as platform-level.

Non-state entries are identified by SIPRI's own labels: names ending in "*"
are non-state armed groups, names ending in "**" are international
organizations, plus "unknown supplier(s)" and "unknown recipient(s)". They
are kept as nodes in all main results, following SIPRI's practice.

Input:  data/processed/deliveries_clean.csv
Output: output/tables/table5_platform_only.csv
        output/tables/check_component_share.csv
        output/tables/check_nonstate_share.csv
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
YEARS = [2005, 2010, 2015, 2020, 2025]

COMPONENT_CATEGORIES = ["Engines", "Sensors"]


def classify(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["level"] = df["Armament category"].apply(
        lambda x: "component" if x in COMPONENT_CATEGORIES else "platform"
    )
    return df


def is_nonstate(names: pd.Series) -> pd.Series:
    return names.str.endswith("*") | names.str.startswith("unknown")


def table5_platform_only(df: pd.DataFrame) -> pd.DataFrame:
    """Recomputes the three Table 1/3 measures with component-level ties
    removed, next to the full network for comparison."""
    rows = []
    for year in YEARS:
        d = df[df["Delivery year"] == year]
        for network, subset in [("Full", d), ("Platform-only", d[d["level"] == "platform"])]:
            m = km.network_measures(km.aggregate_edges(subset))
            rows.append({
                "year": year, "network": network,
                "density": round(m["density"], 4),
                "centralization": round(m["centralization"], 4),
                "hhi": round(m["hhi"], 4),
                "n_nodes": m["n_nodes"], "n_edges": m["n_edges"],
            })
    return pd.DataFrame(rows)


def component_share_over_time(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        d = df[df["Delivery year"] == year]
        comp_tiv = d[d["level"] == "component"]["TIV delivery values"].sum()
        plat_tiv = d[d["level"] == "platform"]["TIV delivery values"].sum()
        total = comp_tiv + plat_tiv
        rows.append({
            "year": year,
            "component_tiv": round(comp_tiv, 1),
            "platform_tiv": round(plat_tiv, 1),
            "component_share_pct": round(100 * comp_tiv / total, 2),
        })
    return pd.DataFrame(rows)


def nonstate_share_over_time(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        edges = km.aggregate_edges(df[df["Delivery year"] == year])
        involved = is_nonstate(edges["supplier"]) | is_nonstate(edges["recipient"])
        rows.append({
            "year": year,
            "nonstate_ties": int(involved.sum()),
            "total_ties": len(edges),
            "tie_share_pct": round(100 * involved.mean(), 2),
            "tiv_share_pct": round(100 * edges.loc[involved, "tiv"].sum() / edges["tiv"].sum(), 2),
        })
    return pd.DataFrame(rows)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DELIVERIES_PATH)
    df = classify(df)

    table5 = table5_platform_only(df)
    table5.to_csv(TABLES_DIR / "table5_platform_only.csv", index=False)

    component_share = component_share_over_time(df)
    component_share.to_csv(TABLES_DIR / "check_component_share.csv", index=False)

    nonstate_share = nonstate_share_over_time(df)
    nonstate_share.to_csv(TABLES_DIR / "check_nonstate_share.csv", index=False)

    print("Table 5 (full vs. platform-only network):")
    print(table5.to_string(index=False))
    print()
    print("Component (engines + sensors) share of total TIV:")
    print(component_share.to_string(index=False))
    print()
    print("Ties and TIV involving non-state or unknown entries:")
    print(nonstate_share.to_string(index=False))


if __name__ == "__main__":
    main()
