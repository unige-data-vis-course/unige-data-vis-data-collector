# UNIGE data viz data colelctor

This project is about importing data from various sources, to feed a data visualization course projects.





## Sources
## GapMinder


Git update the data with

    cd data
    got clone https://github.com/open-numbers/ddf--gapminder--fasttrack.git

### Generate you own Gapminder data subset

List the available concepts

    PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/gapminder_build_local.py --list-concepts



    PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/gapminder_build_local.py \
                   --collate-measures=gini,lex,gdp_pcap \
                   --countries \
                   --output=out

## Development

- Install local python with `.venv` module (base is 3.13).
    
    pip install -r requirements.txt

Unit tests are run with `pytest`.

### Git pre-commit hooks
This repo provides local Git hooks under `.githooks/` to lint and run tests on every commit.

Enable them once in this repository:

```
git config core.hooksPath .githooks
```

What runs on commit:
- Lint: `flake8` excluding `dist,build,venv,.venv,tmp,out`
- Tests: `pytest` on the `tests/` directory

You can run the scripts manually too:

```
.githooks/pre-commit-lint
.githooks/pre-commit-tests
```

Make sure your environment has the dev dependencies installed:

```
pip install -r requirements.txt
```
