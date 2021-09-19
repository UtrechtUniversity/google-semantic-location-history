# fake-google-semantic-location-history

Generate fake Google Semantic Location History (GSLH) data using the python libraries [GenSON](https://pypi.org/project/genson/), [Faker](https://github.com/joke2k/faker), and [faker-schema](https://pypi.org/project/faker-schema/).

First, generate a JSON schema from a JSON object using `GenSON's SchemaBuilder` class. The JSON object is derived from an example GSLH data package, downloaded from Google Takeout. The GSLH data package consists of monthly JSON files with information on e.g. geolocations, addresses and time spend in places and in activity. The JSON schema describes the format of the JSON files, and can be used to generate fake data with the same format. This is done by converting the JSON schema to a custom schema expected by `faker-schema` in the form of a dictionary, where the keys are field names and the values are the types of the fields. The values represent available data types in `Faker`, packed in so-called providers. `Faker` provides a wide variety of data types via providers, for example for names, addresses, and geographical data. This allows us to easily customize the faked data to our specifications.

## Installation
This project makes use of [Poetry](https://python-poetry.org/) for managing dependencies. You can simply install the dependencies with: 

`poetry install`

## Run tests
The current version has been tested with Python 3.9.5. To run the unit tests:

`poetry run pytest`

Note that the `poetry run` command executes the given command inside the project’s virtualenv.

## Run software
`poetry run python google_semantic_location_history/simulation_gslh.py`

This creates a zipfile with the simulated Semantic Location History data in `Location History.zip`.
