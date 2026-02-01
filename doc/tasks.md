# Tasks

# General
  * [x] Create a github action CI/CD to lint with flake8, excluding dist,build,venv,.venv,tmp,out
  * [x] create a github action to run the unit tests
  * [x] create 2 git pre-commit hooks to lint (excluding dist,build,venv,.venv,tmp,out) and run the unit tests


## MeteoSwiss importer

  * [x] Import the list of stations with record and forecast data
  * [x] The list of stations should be downloaded from meteoswiss web resources, not locally
  * [x] In the unit test, stations lists should be loaded from the files in the test/unige_data_vis_data_collector/meteoswiss/resources directory, not from the web
  * [ ] for a given station, read the recorded data
    * use STAC discovery API to get the link to the recorded data
    * load from internet (and mock the calls for unit tests)
    * return a pandas dataframe with the recorded data
    * can be given a date time from which to start the loading of recorded data
    * can be given a recording window (10 minutes, hourly, daily, etc. )
  * [ ] I want a script that pulls the recorded data for all stations
    * the script should be named meteoswiss_recording_pull.py
    * It should use argparse to get the recording window and the start date time
    * It should load data from the web (stations list and recorded data)
    * It can have an option to save the data in a local csv file. If not given, the data should be printed on the screen
    