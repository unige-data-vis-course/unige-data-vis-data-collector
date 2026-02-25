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

# Gapminder
- [x] in unige_data_vis_data_collector/gampinder, create a GapminderImporter service that takes a source_dir:str as a constructor argument
- [x] in GapminderImporter, implement a function load_concepts()->GapminderConcepts
  - reads from source_dir/ddf-concepts.csv
  - parse the csv file and build a GapMinder from each row. Row headers are to be matched to Gapminder object fields
    - concept -> id
    - concept_type -> type
    - updated -> updated_at
    - name_short -> name
    - name -> description_short
    - description -> description
  - Example:
```
concept,concept_type,source_url,version,updated,name_short,name,name_catalog,description,unit,tags,color,format,scales,domain,indicator_url,drill_up
gini,measure,http://gapm.io/ddgini,v4,October 7 2021,Gini,Gini coefficient,,Gini shows income inequality in a society. A higher number means more inequality.,Coefficient,inequality,,,,,,
journakilled,measure,http://gapm.io/djournalists_killed,v5,October 8 2024,Journalists killed,Number of journalists killed,,Number of journalists killed in given year.,People,media,,,,,,
cliberities_fh,measure,http://gapm.io/dfreedom_fh,v4,March 27 2023,Civil Liberties index (FH),Civil Liberties index (FH),,"Civil liberties are assessed by 15 indicators taking a form of questions  and gouped into 4 subcategories                                                                                                                                    A.Freedom of Expression and Belief (0-16 points)                                                                                                                                                                                                                                                           1. Are there free and independent media?                                                                                                                                                                                                                                                          2.Are individuals free to practice and express their religious faith or nonbelief in public and private?                                                                                                                                                                       3.Is there academic freedom, and is the educational system free from extensive political indoctrination?                                                                                                                                              4.Are individuals free to express their personal views on political or other sensitive topics without fear of surveillance or retribution?                                                                                                                                                                             B.Associational and Organizational Rights (0-12 points)                                                                                                                                                                                                                                                          1.Is there freedom of assembly?                                                                                                                                                                                                                                                               2.Is there freedom for nongovernmental organizations, particularly those that are engaged in human rights– and governance-related work?                                                                                                                                                             3.Is there freedom for trade unions and similar professional or labor organizations?                                                                                                                                                                                                                                                        C.Rule of Law (0-16 points)                                                                                                                                                                                                                                                                    1.Is there an independent judiciary?
2.Does due process prevail in civil and criminal matters?                                                                                                                                                                                                                                                                                     3.Is there protection from the illegitimate use of physical force and freedom from war and insurgencies?                                                                                                                                                                                                                                                          4.Do laws, policies, and practices guarantee equal treatment of various segments of the population?
C.Personal Autonomy and Individual Rights (0-16 points)                                                                                                                                                                                                                                                          1.Do individuals enjoy freedom of movement, including the ability to change their place of residence, employment, or education?                                                                                                                                                                           2.Are individuals able to exercise the right to own property and establish private businesses without undue interference from state or nonstate actors?
3.Do individuals enjoy personal social freedoms, including choice of marriage partner and size of family, protection from domestic violence, and control over appearance?
4.Do individuals enjoy equality of opportunity and freedom from economic exploitation?                                                                                                                                                                                                                                               A rating ranged from 1 to 7 with 1 representing the greatest degree of freedom and 7 the smallest degree of freedom; is assigned to a country based on the total scores of civil liberties questiona in the follwing way: score of 53-60 is given a ranting of 1,44-52=>2,  35-43=>3, 26-34=>4,  17-25=>5, 8-16=>6,  0-7=>7                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          ",rating,freedom_fh,,,,,,
demox_eiu,measure,http://gapm.io/ddemocrix_eiu,v4,April 6 2021,Democracy index (EIU),Democracy index (EIU),,"This democracy index is using the data from the Economist Inteligence Unit to express the quality of democracies as a number between 0 and 100. It's based on 60 different aspects of societies that are relevant to democracy universal suffrage for all adults, voter participation, perception of human rights protection and freedom to form organizations and parties.
The democracy index is calculated from the 60 indicators, divided into five ""sub indexes"", which are:
1. Electoral pluralism index;
2. Government index;
3. Political participation indexm;
4. Political culture index;
5. Civil liberty index.
The sub-indexes are based on the sum of scores on roughly 12 indicators per sub-index, converted into a score between 0 and 100.
(The Economist publishes the index with a scale from 0 to 10, but Gapminder has converted it to 0 to 100 to make it easier to communicate as a percentage.)",Percent,democracy_eiu,,percent,,,,
```
  * [x] for a given station, read the recorded data
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

# City streets
- [x] in city_streets package, create a service that loads all streets segment for a given city from https://overpass-turbo.eu/. 
  - It must load the segments by slice of 100 until there are no more.
  - Build a object (@dataclass(frozen=True)) that represents a street segment. it must map the overpass-turbo output structure.
  - concatenate all the segments into a single list
- [x] implement the script city_streets_loader.py that loads all street segments for a given city (example "Nyon") and savec the list as JSON in a file
- [x] Create the script to create a sqlite database with three tables, to store the WaySegment and Ways. Here is the structure
  - points, to store Point: 
    - id_segment: int: a reference to the segment id in the segments table
    - lat (flaot): latitude
    - lon (float): longitude
  - segments:
    - id (int): a unique identifier for the segment
    - street_name (str): the reference to the street name in the streets table
    - nb_lanes (nullable int): the number of lanes in the segment (can be null if not available)
    - max_speed (nullable int): the maximum speed in km/h (can be null if not available)
  - streets:
    - name (str): the stree name, which is unique
    - is_people_name (bool): whether the street name is a people name (True) or otherwise (False)
    - gender_name (nullable str): the gender of the street name (can be null if not available). Will take a value among (NULL, 'MALE', 'FEMALE', 'NEUTRAL')
- [x] Create a script to load the data in the database from the JSON files created by the script city_streets_loader.py. The script should:
  - by default, load all files in out/city_streets_*.jsonl files
  - by default load in the database file databases/city_streets.db
  - create the database if it does not exist
  - use argparse to allow to displa the files to load and the database file to use
  - load WaySegment from a jsonl file saved by the script city_streets_loader.py. example line
    {"type": "way", "id": 4077020, "bounds": {"minlat": 46.2052711, "minlon": 6.1576694, "maxlat": 46.2055108, "maxlon": 6.1579247}, "nodes": [2284328095, 12504558750, 963933493, 2839507], "geometry": [{"lat": 46.2052711, "lon": 6.1579247}, {"lat": 46.2053695, "lon": 6.1578192}, {"lat": 46.2054154, "lon": 6.15777}, {"lat": 46.2055108, "lon": 6.1576694}], "tags": {"cycleway:right": "lane", "cycleway:right:start_date": "2020-06", "highway": "residential", "lanes": "3", "lanes:backward": "1", "lanes:forward": "2", "lit": "yes", "name": "Rue du 31-Décembre", "sidewalk": "both", "surface": "asphalt"}}
  - if the WaySegment already exists (based on id) in the database, skip it.
  - insert the Way Segment in the database, ensuring the uniqueness of street_name and id_segment
- [x] in the database, alter the segment table to add a column to store the city name. Adapt schema and loading scripts accordingly
  - you can recreate the database from scratch. Do not bother with altering the schema of the existing database. 
- [x] in PeopleGenderInferenceService, I want a script that will infer if a stree name is a people reference and if yes, tell me the gender NEUTRAL|MALE|FEMALE. thegender is None if the name is not refering to a people.
  - the script should call an LLM via langchain. LLM model is hosted on Microsoft Azure
  - I can pass a list of street names
  - the script shall strictly return a JSON array. Each element containing the fields street_name, is_people, gender
  - use Pydantic to define/parse the output type
- [x] I want a script to annotate the database with the inferred gender for each street name. The script should:
  - load the database from the sqlite file databases/city_streets.db
  - for each street name in the database, call the PeopleGenderInferenceService to get the is_people and gender
  - update the database with the ispeople and gender for each street name
  - proceed by batches of by default 500 street names
  - display the progress in the console with tdqm
- [ ] in PeopleGenderInferenceService, use Pydantic to parse the output of the LLM cal (list[StreetPeopleGenderInferenceItem)]) and provide pydantic instructions to the LLM
- make a script `city_streets_db_to_csv.py` that converts the sqlite database to a list of csv files.
  - points.csv, segments.csv, streets.csv
  - by default, save the files in `out/city_streets_csv/`
  - by default, load the database from databases/city_streets.db
  - 