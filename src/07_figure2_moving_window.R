# 07_figure2_moving_window.R
#
# Figure 2: out-degree centralization and HHI over rolling five-year
# windows, 2008-2025, as published. Plots the values computed by
# 05_moving_window.py (run that first), so the figure and the CSV share
# one source of numbers.
#
# Input:  output/tables/figure2_moving_window.csv
# Output: output/figures/figure_2_moving_window.png
#
# Run from the project root or from src/:  Rscript 07_figure2_moving_window.R

suppressPackageStartupMessages(library(tidyverse))
# The title's en dash is printed as "..." when Rscript starts in a non-UTF-8
# locale (the default in many terminals); this has no effect where it is unavailable.
invisible(suppressWarnings(Sys.setlocale("LC_CTYPE", "en_US.UTF-8")))

project_root <- if (basename(getwd()) == "src") ".." else "."
ma_results   <- read_csv(file.path(project_root, "output/tables/figure2_moving_window.csv"),
                         show_col_types = FALSE)
figures_dir  <- file.path(project_root, "output/figures")
dir.create(figures_dir, recursive = TRUE, showWarnings = FALSE)

ma_long <- ma_results %>%
  select(Year = window_end, centralization, hhi) %>%
  pivot_longer(cols = c(centralization, hhi),
               names_to = "metric", values_to = "value") %>%
  mutate(metric = recode(metric,
                         centralization = "Out-degree centralization",
                         hhi            = "HHI"))

p <- ggplot(ma_long, aes(x = Year, y = value)) +
  geom_line(linewidth = 1, color = "steelblue") +
  geom_point(size = 1.2, color = "steelblue") +
  facet_wrap(~metric, scales = "free_y") +
  scale_x_continuous(breaks = seq(2008, 2025, 3)) +
  labs(x = "Window end year", y = "Value",
       title = "Supplier concentration, five-year moving average, 2008–2025") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

out <- file.path(figures_dir, "figure_2_moving_window.png")
ggsave(out, p, width = 9, height = 4, dpi = 300, bg = "white")
cat(basename(out), "saved\n")
