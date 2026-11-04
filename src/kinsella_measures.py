"""
kinsella_measures.py

Network measures shared by the numbered scripts, so that every table,
robustness check and figure uses the same formulas. Equation numbers refer
to the paper's Method section; equations 1-4 follow Kinsella (2003, 18-20).

  out-degree d_O(n_i), in-degree d_I(n_j)            (eq. 1)
      number of distinct recipients / suppliers in the cross-section
  density                                              (eq. 2)
      = (sum of out-degrees + sum of in-degrees) / g(g-1)
      = 2L / g(g-1)   -- each directed tie is counted once as an out-degree
                         and once as an in-degree, as in Kinsella's formula
  out-degree centrality (normalized)                   (eq. 3)
      = d_O(n_i) / (g-1)
  group centralization                                 (eq. 4)
      = sum_i [d_O(n_max) - d_O(n_i)] / (g-1)^2   -- raw out-degrees
  HHI                                                  (eq. 5)
      = sum_i s_i^2,  s_i = supplier i's share of total TIV

g is the number of actors with at least one arms-transfer tie in the
network being measured; L is the number of directed supplier-recipient ties.
Degree-based measures use only the existence of ties; TIV enters only the HHI.
"""

import pandas as pd
import networkx as nx


def aggregate_edges(deliveries: pd.DataFrame) -> pd.DataFrame:
    """Collapses SIPRI delivery rows into one weighted edge per
    supplier-recipient pair (weight = summed TIV). Multiple transfers of
    different weapon categories between the same pair become a single edge."""
    return (
        deliveries.groupby(["Supplier", "Recipient"])["TIV delivery values"]
        .sum()
        .reset_index()
        .rename(columns={
            "Supplier": "supplier",
            "Recipient": "recipient",
            "TIV delivery values": "tiv",
        })
    )


def build_graph(edges: pd.DataFrame) -> nx.DiGraph:
    G = nx.DiGraph()
    for _, row in edges.iterrows():
        G.add_edge(row["supplier"], row["recipient"], weight=row["tiv"])
    return G


def density(G: nx.DiGraph) -> float:
    g = G.number_of_nodes()
    return 2 * G.number_of_edges() / (g * (g - 1))


def out_degree_centrality(G: nx.DiGraph) -> dict:
    g = G.number_of_nodes()
    return {n: d / (g - 1) for n, d in G.out_degree()}


def centralization(G: nx.DiGraph) -> float:
    g = G.number_of_nodes()
    outdeg_raw = dict(G.out_degree())
    d_max = max(outdeg_raw.values())
    return sum(d_max - d for d in outdeg_raw.values()) / ((g - 1) ** 2)


def supplier_shares(edges: pd.DataFrame) -> pd.Series:
    """Each supplier's share of total TIV, largest first."""
    supplier_tiv = edges.groupby("supplier")["tiv"].sum()
    return (supplier_tiv / supplier_tiv.sum()).sort_values(ascending=False)


def hhi(edges: pd.DataFrame) -> float:
    return float((supplier_shares(edges) ** 2).sum())


def network_measures(edges: pd.DataFrame) -> dict:
    """Density, centralization and HHI (plus network size) for one edge list."""
    G = build_graph(edges)
    return {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "density": density(G),
        "centralization": centralization(G),
        "hhi": hhi(edges),
    }
