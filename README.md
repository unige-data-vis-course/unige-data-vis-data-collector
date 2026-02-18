# UNIGE data viz data colelctor

This project is about importing data from various sources, to feed a data visualization course projects.





## Sources
### GapMinder

Git update the data with

    cd data
    got clone https://github.com/open-numbers/ddf--gapminder--fasttrack.git

### Generate you own Gapminder data subset

List the available concepts

    PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/gapminder_build_local.py \
                   --list-concepts

Build a csv (with a is_forecast column) for a selected list of indicators. `--countries` also get the countries list + dimensions.
Results are saved in `out/` directory.

    PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/gapminder_build_local.py \
                   --collate-measures=gini,lex,gdp_pcap,child_mortality_0_5_year_olds_dying_per_1000_born,children_per_woman_total_fertility \
                   --countries \
                   --output=out

### Kanban simulator
The goal is to simulate a ticket list evolution on a kanban board

## Development

- Install local python with `.venv` module (base is 3.13).
    
    pip install -r requirements.txt

Unit tests are run with `pytest`.

### Pre-commit hooks (DevSecOps)
This repo uses `pre-commit` to run security checks locally before each commit.

What runs on commit:
- Gitleaks: secret scanning with redaction
- Bandit: Python security static analysis over `src/` (excluding `tests, venv, .venv, tmp, out, build, dist`) with minimum severity and confidence set to `medium`.

Setup once per machine:

```
pip install pre-commit
pre-commit install
```

Run on all files (optional, e.g., first time):

```
pre-commit run --all-files
```

Configuration lives in `.pre-commit-config.yaml`. The CI also runs the same checks via GitHub Actions.
