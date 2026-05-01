# User Stories — Geneva Tree Inventory Teaching Notebook

**Audience for this brief:** Claude Code, implementing the notebook end-to-end.
**Audience for the notebook itself:** Third-year computational-sciences students at the University of Geneva, with a biology background, basic Python, limited software-craftsmanship habits, and no prior R or ggplot2 exposure assumed.

---

## 0. Global conventions (apply to every story)

These are project-wide decisions. If any of them are wrong for the course, change them here first, then propagate.

- **Format:** One Quarto notebook (`tree_inventory_geneva.qmd`) rendered to self-contained HTML. Each of the ten stories below becomes one top-level `##` section, in order.
- **Language:** All prose, code comments, and chart text in **English**. (Course is delivered in English; if French is needed it will be a separate translation pass.)
- **Project layout:**
  ```
  /
    tree_inventory_geneva.qmd   # the notebook
    R/                          # helper functions sourced by the notebook
    data/
      raw/                      # original SHP bundle, never modified
      processed/                # GeoPackage produced by Story 1
    renv.lock                   # pinned dependencies
    README.md                   # how a student runs this
  ```
- **Reproducibility:** Use `renv` from the start. Pin R ≥ 4.3 and the tidyverse, sf, ggplot2, patchwork, scales, viridis, treemapify, gganimate stack.
- **Style:** Tidyverse style, native pipe `|>` (not `%>%`), explicit package prefixes the first time a function appears in each section (`sf::st_read()`), then unprefixed afterwards.
- **Pedagogical voice:** Every section opens with a 2–4 sentence prose intro that names the *learning objective* and the *grammar-of-graphics concept* introduced. Every chart is followed by a short "what to look at" caption. No section ends silently — always a one-paragraph transition into the next.
- **Charts:** ggplot2 only (no base graphics, no plotly), `theme_minimal(base_size = 12)` as default, `viridis` for sequential/ordered colour, `colorblind`-safe palettes everywhere. Every chart has a sentence-style title, an informative subtitle, axis labels with units, and an explicit `caption =` field crediting SITG.
- **Data source:** SITG dataset `SIPV_ICA_ARBRE_ISOLE` (Inventaire cantonal des arbres isolés). The notebook must download it programmatically on first run if `data/raw/` is empty; a hardcoded URL constant near the top makes it easy to update.
- **CRS:** Original data is CH1903+ / LV95 (EPSG:2056). Keep the working copy in 2056 for area/distance calculations; reproject to WGS84 (EPSG:4326) only for web-style maps.
- **Verification:** Each story ends with a small sanity-check chunk (an `stopifnot()` or printed assertion) so students know the previous step actually produced the expected object.

---

## STORY-01 — Project bootstrap and data acquisition

**As a** student opening the notebook for the first time,
**I want** the project to set itself up, download the cantonal tree dataset, and convert it into a clean working file,
**so that** I can focus on visualisation in the following sections without fighting paths or formats.

**Acceptance criteria:**
- A `setup` chunk loads all required packages and prints their versions.
- If `data/raw/SIPV_ICA_ARBRE_ISOLE.shp` is absent, the notebook downloads the SITG zip, unpacks it into `data/raw/`, and verifies the four canonical sibling files exist (`.shp`, `.shx`, `.dbf`, `.prj`).
- The shapefile is read once with `sf::st_read()` and immediately rewritten as `data/processed/trees_geneva.gpkg`.
- The notebook explains, in 3–5 sentences of prose, what each shapefile sibling is and *why* the immediate conversion to GeoPackage is good practice (UTF-8, single file, no 10-character field-name truncation).
- A final assertion confirms the GPKG exists and has > 200,000 features.

**Technical hints:** `download.file()`, `utils::unzip()`, `sf::st_layers()`, `sf::st_write(..., delete_dsn = TRUE)`. Use `here::here()` for all paths.

---

## STORY-02 — Data hygiene and the honesty of provenance

**As a** student about to make charts from this data,
**I want** to inspect its structure, completeness, and known accuracy limits,
**so that** every later visualisation is informed by what the data can and cannot say.

**Acceptance criteria:**
- Print `dplyr::glimpse()` and a tidy summary table of column types, non-NA counts, and example values.
- A `naniar::vis_miss()` (or equivalent ggplot) view of missingness across columns.
- Histograms of `hauteur`, `diametre_tronc`, `diametre_couronne` with sensible binning and axis units (metres, centimetres).
- A short prose box explicitly stating the **~25 m vs ~1 m positional accuracy** split between the 1976 inventory and modern surveys, with a small bar chart showing record counts per decade of survey if such a column exists (otherwise per plantation decade as a proxy, with a clear caveat).
- A boxed "What this means for our charts" paragraph listing 2–3 concrete consequences for later sections.

**Pedagogical anchor:** *Every chart inherits the sins of its data.* Introduce the concept of provenance and uncertainty before any aesthetic mapping is shown.

---

## STORY-03 — Univariate distributions and the grammar of a basic chart

**As a** student new to ggplot2,
**I want** to build histograms and density plots of single variables step by step,
**so that** I internalise the layered grammar (data → aesthetic → geom → stat → scale → theme).

**Acceptance criteria:**
- Build one chart incrementally across **at least four code chunks**, each adding exactly one layer or scale, with a one-sentence explanation between chunks.
- Compare the same variable (`hauteur`) under three different `binwidth` values and discuss how bin choice changes the perceived story.
- Show `geom_density()` as an alternative and articulate when to prefer it.
- Free axis units, log10 scale comparison for `diametre_tronc` (motivate with the wide range).
- Final chart uses `labs(title = ..., subtitle = ..., caption = "Source: SITG, ICA")`.

**Pedagogical anchor:** The *grammar* of graphics — make the layer-by-layer build visible.

---

## STORY-04 — Categorical encoding for high-cardinality data

**As a** student facing 200+ tree species,
**I want** to compare three encodings of "top species" and see why some work and others don't,
**so that** I learn to match a chart type to the perceptual task.

**Acceptance criteria:**
- Compute `top20 <- count(trees, genre_espece, sort = TRUE) |> slice_head(n = 20)`.
- Produce three side-by-side charts using `patchwork`:
  1. Ordered bar chart (`fct_reorder`).
  2. Lollipop chart.
  3. `treemapify::geom_treemap()` of the **full** species list.
- One paragraph explicitly invoking the **Cleveland & McGill ranking** of perceptual tasks to justify why the ordered bar wins for ranking and the treemap wins for part-of-whole-with-long-tail.
- Show, as a counter-example, a deliberately bad pie chart of the top 20 with `coord_polar()` and call out what fails about it (no shaming, just observation).

**Pedagogical anchor:** Ordering > colour. Encoding follows task.

---

## STORY-05 — Bivariate relationships, overplotting, and an allometric law

**As a** student with biology background,
**I want** to fit a DBH–height relationship and battle overplotting,
**so that** I see how the grammar of graphics scales from one variable to two and connects to a real biological model.

**Acceptance criteria:**
- Build `geom_point()` first to demonstrate the overplotting problem (~237k points).
- Iterate: `alpha = 0.02`, then `geom_hex(bins = 60)`, then `geom_density_2d()`.
- Add `geom_smooth(method = "lm", formula = y ~ log(x))` and explain in one short paragraph that this is the **allometric scaling law** H = a · DBHᵇ on a log-x axis.
- `facet_wrap(~ genre_espece)` over the **six most abundant species**, with free y axis discussed (kept fixed for comparability — explain the choice).
- A small table comparing the per-species slope coefficients, computed with `broom::tidy()`.

**Pedagogical anchor:** Grammar layers naturally; biology supplies the model.

---

## STORY-06 — First spatial visualisation with `sf`

**As a** student who has never made a map in R,
**I want** to project tree points onto cantonal communes,
**so that** I learn that maps are charts — same grammar, new geometry.

**Acceptance criteria:**
- Print `sf::st_crs(trees)` and explain the EPSG:2056 result in one sentence.
- Download the SITG cantonal communes layer (or use a bundled GeoJSON in `data/raw/`) and load with `st_read()`.
- Build the map with two layered `geom_sf()` calls: communes first (light fill, thin stroke), trees second (`alpha = 0.05`, `size = 0.1`).
- Add `coord_sf()` with explicit limits framing the canton.
- Demonstrate a reprojection to WGS84 and overlay on a `ggspatial::annotation_map_tile()` background as a contrasting "web map" version, with a one-paragraph reflection on what each version is *for*.

**Pedagogical anchor:** Maps are charts. CRS is a design choice.

---

## STORY-07 — Density mapping and the detail/pattern trade-off

**As a** student trying to communicate canopy distribution,
**I want** to see the same data as raw dots, hex-binned counts, and a kernel-density surface,
**so that** I understand what each representation answers and hides.

**Acceptance criteria:**
- Three maps of the same trees, side by side via `patchwork`:
  1. Raw `geom_sf()` dots.
  2. `stat_binhex()` on projected coords, viridis fill, count legend.
  3. `stat_density_2d_filled()` with at least 8 levels.
- Below the figure, a paragraph titled "Which question does each map answer?" mapping each chart to the question it serves (location of an individual tree vs distribution of canopy mass).
- Explicit mention of **Bertin's visual variables** (position, size, value, hue) and how each map exploits a different one.

**Pedagogical anchor:** Detail vs pattern. The same data supports different questions.

---

## STORY-08 — Time, cohorts, and the chart of what's missing

**As a** student tempted to read history off plantation dates,
**I want** to first measure and visualise the missingness of those dates,
**so that** I do not mistake recording bias for a real trend.

**Acceptance criteria:**
- Histogram of `date_plantation` by decade.
- Cumulative-plantings curve over time (`geom_step` of cumulative count).
- A **missingness chart**: proportion of `NA` plantation dates by tree-height bucket, computed with `cut(hauteur, c(0, 5, 10, 20, 40))` and shown as an ordered bar chart.
- Side-by-side display of "the chart of what we know" vs "the chart of what we don't know", with a 2-paragraph commentary explicitly arguing that the second chart is *more honest* than the first.

**Pedagogical anchor:** Missing data is data. Surface it before interpreting trends.

---

## STORY-09 — A Gapminder-style storytelling chart

**As a** student who has been shown Hans Rosling's bubble charts repeatedly in lectures,
**I want** to build one from this dataset by joining commune-level socio-economic data,
**so that** I practise synthesising several variables into a single, story-driven figure.

**Acceptance criteria:**
- Aggregate the inventory to commune level: tree count, trees per inhabitant, Shannon species-diversity index.
- Join with at least one commune-level statistic from the **Office cantonal de la statistique (OCSTAT)** — population is sufficient if a richer indicator is unavailable; document the source in the caption.
- Bubble chart: x = trees per inhabitant, y = Shannon diversity, size = population, colour = an OCSTAT region or grouping.
- Use `ggrepel::geom_text_repel()` to label only the 5–8 most extreme communes (not all of them).
- A **sentence-style headline title** that states the finding ("Geneva's wealthier suburbs have more trees per resident but less species variety", or whatever the data actually shows — Claude Code must compute this and not invent it).
- 150-word caption block written *after* the chart is built, defending the chosen story.
- Optional stretch: `gganimate` over plantation cohorts.

**Pedagogical anchor:** Synthesis + narrative. The chart's title is the conclusion, not the variable name.

---

## STORY-10 — Critique and redesign capstone

**As a** student finishing the course,
**I want** to recreate one existing public visualisation of the ICA data and then redesign it using everything we learned,
**so that** I demonstrate I can apply principles, not just produce charts.

**Acceptance criteria:**
- Embed (as a static screenshot or a faithful ggplot2 reproduction) one public visualisation of the ICA data — for example from the SITG online viewer or the Portraits des Géants project.
- Build a **redesigned** version in ggplot2 that explicitly addresses at least three named principles from the course (e.g., Cleveland-McGill task hierarchy, pre-attentive attributes, colour-blind safety with `colorspace::check_palette()`, removal of chartjunk à la Tufte).
- Display the two side by side with `patchwork` under the headers "As published" and "Redesigned".
- A short justification table — three columns: principle invoked, change made, expected effect on the reader.
- Final paragraph: one honest concession ("here is what the original does *better* than my redesign"). Avoid triumphalism; this is a critique exercise, not a takedown.

**Pedagogical anchor:** Integration of every prior concept. Honest critique includes self-critique.

---

## Cross-cutting notes for Claude Code

- **Do not pre-compute or cache** intermediate objects across sections in a way that hides the dependency on prior chunks. Each section should run after its predecessors but make its inputs explicit in the first chunk.
- **No `install.packages()` calls inside the notebook.** Dependencies live in `renv.lock` and are restored once via `renv::restore()`, documented in `README.md`.
- **No emojis** anywhere in the notebook output, code comments, or chart text.
- **Word counts in prose blocks matter.** Where a story specifies "150 words" or "2 paragraphs", respect it — verbosity is the enemy of pedagogy here.
- **Verify before declaring done.** After implementation, render the notebook end to end into HTML, confirm zero warnings beyond the documented sf CRS notices, and confirm every chart actually displays. Report any story whose acceptance criteria could not be met fully and why.
- **README.md** must explain in under 30 lines how a fresh student clones the repo, runs `renv::restore()`, and renders the notebook.

---

## Suggested order of implementation

Stories 01 → 02 → 03 are foundational and unblock everything. Stories 04, 05, 06 can be implemented in parallel once the data is loaded. Stories 07 depends on 06; 08 is independent; 09 depends on 06 and an external data download; 10 is the capstone and should be implemented last.
