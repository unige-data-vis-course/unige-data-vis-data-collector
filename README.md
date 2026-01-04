# UNIGE data viz data colelctor

This project is about importing data from various sources, to feed a data visualization course projects.



## Sources
### MeteoSwiss
The goal is to import weather data and forecasts from MeteoSwiss, for all recording/forecasting stations.

## Development

- Install local python with `venv` module (base is 3.13).
- tests are run with `pytest`.
- 
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
