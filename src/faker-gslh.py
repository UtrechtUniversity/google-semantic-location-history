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


def get_faker_schema(json_schema, iterations=1):
    if "type" not in json_schema:
        key = next(iter(json_schema))
        value = get_faker_schema(json_schema[key])
        print(key)
        return {key: value}
    elif json_schema['type'] == "object":
        value = {}
        for prop, val in json_schema["properties"].items():
            value.update(get_faker_schema({prop: val}))
    elif json_schema['type'] == "array":
        value = [get_faker_schema(json_schema['items']) for i in range(iterations)]
    elif json_schema['type'] == "string":
        value = "address"
    elif json_schema['type'] == "number":
        value = "address"
    elif json_schema['type'] == "integer":
        value = "local_latlng(country_code=NL)"
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
    schema = get_faker_schema(json_schema["properties"])
    fake = Faker('nl_NL')
    fake.add_provider(geo)
    faker = FakerSchema(faker=fake, locale='nl_NL')
    data = faker.generate_fake(schema)

    return data


if __name__ == '__main__':
    result = process("test/data/Location History.zip")
    print(result)
