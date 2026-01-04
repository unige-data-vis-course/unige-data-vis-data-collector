# Tasks

## MeteoSwiss importer

  * [x] Import the list of stations with record and forecast data
  * [x] The list of stations should be downloaded from meteoswiss web resources, not locally
  * [x] Create a github action CI/CD to lint with flake8 ^, excluding dist,build,venv,.venv,tmp,out
  * [x] In the unit test, stations lists should be loaded from the files in the test/unige_data_vis_data_collector/meteoswiss/resources directory, not from the web