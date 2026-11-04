# 06_figure1_network_maps.R
#
# Figures 1a-1e: arms trade network map for each cross-section, as
# published. Node size and shading are proportional to normalized
# out-degree centrality (number of distinct recipients / (g-1)); only the
# ten most central suppliers are labelled. Positions come from a
# force-directed (Fruchterman-Reingold) layout with a fixed seed and carry
# no substantive meaning.
#
# Ties are binary here (distinct supplier-recipient pairs), matching the
# degree-based measures. Edges are read in SIPRI's row order from
# deliveries_clean.csv, which the layout depends on, so the published
# figures are reproduced exactly.
#
# Input:  data/processed/deliveries_clean.csv
# Output: output/figures/figure_1a_2005.png ... figure_1e_2025.png
#
# Run from the project root or from src/:  Rscript 06_figure1_network_maps.R

suppressPackageStartupMessages({
  library(tidyverse); library(igraph); library(ggraph); library(ggrepel)
})

project_root <- if (basename(getwd()) == "src") ".." else "."
deliveries   <- read_csv(file.path(project_root, "data/processed/deliveries_clean.csv"),
                         show_col_types = FALSE)
figures_dir  <- file.path(project_root, "output/figures")
dir.create(figures_dir, recursive = TRUE, showWarnings = FALSE)

years  <- c(2005, 2010, 2015, 2020, 2025)
labels <- c("1a", "1b", "1c", "1d", "1e")

make_map <- function(y, topLab = 10) {
  e <- deliveries %>%
    filter(`Delivery year` == y,
           !is.na(Supplier), !is.na(Recipient),
           Supplier != "", Recipient != "") %>%
    distinct(Supplier, Recipient)
  g <- graph_from_data_frame(e, directed = TRUE)
  V(g)$cent <- degree(g, mode = "out", normalized = TRUE)
  V(g)$lab  <- ifelse(rank(-V(g)$cent, ties.method = "min") <= topLab, V(g)$name, "")
  set.seed(42)  # fixes the layout so the figures can be reproduced
  ggraph(g, layout = "fr") +
    geom_edge_link(alpha = 0.08, color = "grey70") +
    geom_node_point(aes(size = cent, fill = cent),
                    shape = 21, color = "grey30", stroke = 0.2) +
    geom_node_text(aes(label = lab), repel = TRUE, size = 3, fontface = "bold",
                   bg.color = "white", bg.r = 0.12, max.overlaps = Inf,
                   min.segment.length = 0, segment.color = "grey60", segment.size = 0.2) +
    scale_size(range = c(1, 9), limits = c(0, 0.65), guide = "none") +
    scale_fill_gradient(low = "grey85", high = "grey10", limits = c(0, 0.65), guide = "none") +
    coord_equal() + labs(title = y) + theme_void() +
    theme(plot.title = element_text(hjust = 0.5, face = "bold", size = 12))
}

for (i in seq_along(years)) {
  out <- file.path(figures_dir, sprintf("figure_%s_%d.png", labels[i], years[i]))
  ggsave(out, make_map(years[i]), width = 6, height = 6, dpi = 300, bg = "white")
  cat(basename(out), "saved\n")
}
