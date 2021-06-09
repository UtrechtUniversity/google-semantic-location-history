import json
import itertools
import re
import zipfile

from genson import SchemaBuilder
from faker import Faker
from faker.providers import geo
from faker_schema.faker_schema import FakerSchema

YEARS = [2020]
MONTHS = ["JANUARY"]

# schema with types
SCHEMA_TYPES = {
    'latitudeE7': 'latitude', 
    'longitudeE7': 'longitude',
    'startTimestampMs': 'random_digit_not_null', 
    'endTimestampMs': 'random_digit_not_null', 
    'distance': 'random_digit_not_null', 
    'activityType': 'random_digit_not_null', 
    'confidence': 'random_digit_not_null', 
    'activityType': 'random_digit_not_null', 
    'probability': 'random_digit_not_null',
    'latE7': 'latitude',
    'lngE7': 'longitude',
    'timestampMs': 'random_digit_not_null', 
    'accuracyMeters': 'random_digit_not_null',
    'placeId': 'random_digit_not_null', 
    'name': 'random_digit_not_null', 
    'hexRgbColor': 'random_digit_not_null',
    'address': 'address', 
    'name': 'name',
    'deviceTag': 'random_digit_not_null',
    'locationConfidence': 'random_digit_not_null', 
    'semanticType': 'random_digit_not_null', 
    'startTimestampMs': 'random_digit_not_null', 
    'endTimestampMs': 'random_digit_not_null', 
    'placeConfidence': 'random_digit_not_null', 
    'centerLatE7': 'latitude', 
    'centerLngE7': 'longitude', 
    'visitConfidence': 'random_digit_not_null', 
    'editConfirmationStatus': 'random_digit_not_null',
    'deviceTag': 'random_digit_not_null', 
    'placeConfidence': 'random_digit_not_null', 
    'centerLatE7': 'latitude', 
    'centerLngE7': 'longitude', 
    'visitConfidence': 'random_digit_not_null', 
    'accuracyMeters': 'random_digit_not_null'
}


def get_faker_schema(json_schema, custom=None, iterations=1):
    if "type" not in json_schema:
        key = next(iter(json_schema))
        if isinstance(custom, dict) and key in custom:
            value = custom[key]
        else:
            value = get_faker_schema(json_schema[key], custom=custom)
        return {key: value}
    elif json_schema['type'] == "object":
        value = {}
        for prop, val in json_schema["properties"].items():
            value.update(get_faker_schema({prop: val}, custom=custom))
    elif json_schema['type'] == "array":
        value = [get_faker_schema(json_schema['items'], custom=custom) for i in range(iterations)]
    elif json_schema['type'] == "string":
        value = "pystr_format"
    elif json_schema['type'] == "number":
        value = "pyfloat"
    elif json_schema['type'] == "integer":
        value = "pyint" #"local_latlng(country_code=NL)"
    return value


def process(file_data):
    """Return relevant data from zipfile for years and months
    Args:
        file_data: zip file or object

    Returns:
        dict: dict with summary and DataFrame with extracted data
    """
    builder = SchemaBuilder()

    # Extract info from selected years and months
    with zipfile.ZipFile(file_data) as zfile:
        file_list = zfile.namelist()
        for year in YEARS:
            for month in MONTHS:
                for name in file_list:
                    monthfile = f"{year}_{month}.json"
                    if re.search(monthfile, name) is not None:
                        data = json.loads(zfile.read(name).decode("utf8"))
                        builder.add_object(data)
                        break

    json_schema = builder.to_schema()
    print(json_schema)
    schema = get_faker_schema(json_schema["properties"], custom=SCHEMA_TYPES)
    fake = Faker('nl_NL')
    fake.add_provider(geo)
    faker = FakerSchema(faker=fake, locale='nl_NL')
    data = faker.generate_fake(schema)

    return data


if __name__ == '__main__':
    result = process("test/data/Location History.zip")
    print(result)
