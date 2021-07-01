# fake-google-semantic-location-history

Generate fake Google Semantic Location History data using the packages `genson` <https://pypi.org/project/genson/>, `Faker` <https://github.com/joke2k/faker>, and `faker-schema` <https://pypi.org/project/faker-schema/>.

First, generate a JSON schema from a JSON object using genson's `SchemaBuilder` class. The JSON schema is then converted to a custom schema expected by `faker-schema` in the form of a dictionary, where the keys are field names and
the values are the types of the fields. The schema dictionay can have nested dictionaries and lists too. 
