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
The goal is to simulate a ticket list evolution on a kanban board.
- A ticket status goes from BACKLOG to DEPLOYED via a list of intermediary steps (IN_SCOPING, DONE_SCOPING, IN_DEVELOPMENT...). The full list can be found [here](src/unige_data_vis_data_collector/kanban_simulator/__init__.py)
- we can define a experiment duration, as the number of ticket that will flow through
- We shal define transition period (average of the Poison distrubtion) for each status. These period can be cahnge dynmically through a function of time
- It is possible to define WIP limit (the maximum number of ticket that can be in one status at the given moment). Also setable through functions of time
- the DEPLOYED transition can happen at a given pace (every 7 days, for example) 

The simplest way is to play with the [simulate_kanban.py](src/unige_data_vis_data_collector/scripts/simulate_kanban.py) script.
Parameters as the simulation duration, dynamic WIP etc. are set into the script.

It output two files:
  - [kanban-daily-count-by-status.csv](out/kanban-daily-count-by-status.csv): for each day of the simultion, the number of tickets that falls in each status
  - [kanban-ticket-status-transitions.csv](notebooks/kanban-ticket-status-transitions.csv): For each ticket, the date of all status transitions.


### City streets
The goal is to load city streets data from overpass-turbo API. The shall be saved in a sqlite database and annotated with the gender information if the street name is designing people.

#### Export DB to csv files

To import into Tableau Public. the Sqlite database must be exported to csv files.

    `PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/city_streets_db_to_csv.py`


#### Loading new data into the database
**NB**: do not bother with these steps if you already have the city data in the sqlite database `databases/city_streets.db`

There are several steps:
  - load way segments from overpass-turbo API and saved them in `out/city_streed_CITY.jsonl`

     `PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/city_streets_db_downloader.py --city=Genève,Lausanne`
  - Import all such jsonl files in sqlite database (default is `databases/city_streets.db`)
    
    `PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/city_streets_db_loader.py`
  - annotate the streets table with gender information based on the street name

    `PYTHONPATH=src python src/unige_data_vis_data_collector/scripts/city_streets_db_annotate_people_gender.py`


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
