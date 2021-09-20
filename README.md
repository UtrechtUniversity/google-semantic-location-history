# Google Semantic Location History Faker

<!-- TABLE OF CONTENTS -->
## Table of Contents
- [About the Project](#about-the-project)
- [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Testing](#testing)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contact](#contact)

## About the Project
Generate fake Google Semantic Location History (GSLH) data using the python libraries [GenSON](https://pypi.org/project/genson/), [Faker](https://github.com/joke2k/faker), and [faker-schema](https://pypi.org/project/faker-schema/).

First, we generate a JSON schema from a JSON object using `GenSON's SchemaBuilder` class. The JSON object is derived from an example GSLH data package, downloaded from Google Takeout. The GSLH data package consists of monthly JSON files with information on e.g. geolocations, addresses and time spend in places and in activity. The JSON schema describes the format of the JSON files, and can be used to generate fake data with the same format. This is done by converting the JSON schema to a custom schema expected by `faker-schema` in the form of a dictionary, where the keys are field names and the values are the types of the fields. The values represent available data types in `Faker`, packed in so-called providers. `Faker` provides a wide variety of data types via providers, for example for names, addresses, and geographical data. This allows us to easily customize the faked data to our specifications.

## Getting Started

### Prerequisites
This project makes use of Python 3.9.2 and [Poetry](https://python-poetry.org/) for managing dependencies. 

### Installation
You can simply install the dependencies with 
`poetry install` in the projects root folder.

### Testing
To run the unit tests:

`poetry run pytest`

Note that the `poetry run` command executes the given command inside the project’s virtual environment.

## Usage

`poetry run python google_semantic_location_history/simulation_gslh.py`

This creates a zipfile with the simulated Semantic Location History data in `Location History.zip`.

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

To contribute:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- CONTACT -->
## Contact
[UU Research Engineering team](https://github.com/orgs/UtrechtUniversity/teams/research-engineering) - research.engineering@uu.nl
