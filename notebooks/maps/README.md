# Geneva Tree Inventory — Data Visualisation Notebook

A Quarto notebook for University of Geneva computational-sciences students exploring the SITG cantonal isolated tree inventory (`SIPV_ICA_ARBRE_ISOLE`, 238 000+ trees) through ten progressive visualisation exercises.

## Prerequisites

- R ≥ 4.3
- Quarto ≥ 1.4 (`quarto check`)

## Setup (one time)

```r
# Install renv if needed
install.packages("renv")

# Restore the pinned package library
renv::restore()
```

If `renv.lock` is absent (fresh clone before snapshot), install packages manually:

```r
install.packages(c(
  "here", "sf", "tidyverse", "naniar", "patchwork",
  "scales", "viridis", "treemapify", "gganimate",
  "ggrepel", "broom", "ggspatial", "geodata",
  "colorspace", "lubridate"
))
renv::snapshot()
```

## Rendering

```bash
quarto render tree_inventory_geneva.qmd
```

The output is `tree_inventory_geneva.html` (self-contained, no server needed).

## Data

Raw shapefiles live in `data/SIPV_ICA_ARBRE_ISOLE-SHP/` (bundled) or will be downloaded to `data/raw/` on first render. The notebook converts them to `data/processed/trees_geneva.gpkg` automatically.

Source: SITG — Inventaire cantonal des arbres isolés (SIPV_ICA_ARBRE_ISOLE).  
License: see `data/SIPV_ICA_ARBRE_ISOLE-SHP/DOC/`.
