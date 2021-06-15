import json
import itertools
import re
import zipfile
from datetime import datetime
from collections import OrderedDict

from zipfile import ZipFile
from genson import SchemaBuilder
from faker import Faker
from faker.providers import geo
from faker_schema.faker_schema import FakerSchema
from geopy.distance import geodesic

YEARS = [2020]
MONTHS = ["JANUARY"]
NDAYS = 31
NPLACES = 50
NACTIVITIES = 500
TOP_PLACES = [0.4, 0.3, 0.05]
ACTIVITIES = OrderedDict({
    "CYCLING": 0.3,
    "WALKING": 0.2,
    "IN_VEHICLE": 0.3,
    "IN_TRAIN": 0.2
})
# schema with types
SCHEMA_TYPES = {
    'name': 'company',
    'visitConfidence': 'random_digit_not_null', 
    'accuracyMeters': 'random_digit_not_null'
}


def write_zipfile(data, zipfile):
    """

    """

    with ZipFile(zipfile, 'w') as zip_archive:
        # Create files on zip archive
        with zip_archive.open('Takeout/Location History/Semantic Location History/2021/2021_JANUARY.json', 'w') as file1:
            file1.write(json.dumps(data).encode('utf-8'))
        # with zip_archive.open('Takeout/Location History/Semantic Location History/2020/2020_JANUARY.json', 'w') as file1:
        #     file1.write(json.dumps(data_2020).encode('utf-8'))
        # with zip_archive.open('Takeout/Location History/Semantic Location History/2019/2019_JANUARY.json', 'w') as file1:
        #     file1.write(json.dumps(data_2019).encode('utf-8'))


def get_faker_schema(json_schema, custom=None, iterations={}, parent_key=None):    
    if "type" not in json_schema:
        key = next(iter(json_schema))
        if isinstance(custom, dict) and key in custom:
            value = custom[key]
        else:
            value = get_faker_schema(json_schema[key], custom=custom, iterations=iterations, parent_key=key)
        return {key: value}
    elif json_schema['type'] == "object":
        value = {}
        for prop, val in json_schema["properties"].items():
            value.update(get_faker_schema({prop: val}, custom=custom, iterations=iterations))
    elif json_schema['type'] == "array":
        iters = iterations.get(parent_key, 1)
        value = [get_faker_schema(json_schema['items'], custom=custom, iterations=iterations) for i in range(iters)]
    elif json_schema['type'] == "string":
        value = "pystr_format"
    elif json_schema['type'] == "number":
        value = "pyfloat"
    elif json_schema['type'] == "integer":
        value = "pyint"
    return value

def create_places(total=1):
    fake = Faker('nl_NL')
    fake.add_provider(geo)
    places = {}
    latlon = fake.local_latlng(country_code="NL")
    for number in range(total):
        latitude = fake.unique.coordinate(center=latlon[0], radius=0.1)
        longitude = fake.unique.coordinate(center=latlon[1], radius=0.1)
        place = {
            "name": fake.unique.company(),
            "address": fake.unique.address(), 
            "latitude": float(latitude),
            "longitude": float(longitude)
        }
        places.update({fake.unique.pystr_format(): place})
    return places

def update_data(data, start_date):
    fake = Faker('nl_NL')
    start_time = start_date.timestamp() * 1000
    duration = NDAYS * 24 * 60 * 60 * 1e3 / NACTIVITIES
    duration_place = 0.8 * duration
    duration_activity = 0.2 * duration 
    places = create_places(total=NPLACES)
    elements = OrderedDict()
    for number, place in enumerate(places):
        if number < len(TOP_PLACES):
            elements[place] = TOP_PLACES[number]
        else:
            elements[place] = (1.0 - sum(TOP_PLACES))/(NPLACES - len(TOP_PLACES))
    placeId = fake.random_element(elements=elements)
    start_location = placeId
    for data_unit in data["timelineObjects"]:
        
        end_location = fake.random_element(elements=elements)
        if "placeVisit" in data_unit:
            end_time = start_time + duration_place
            data_unit["placeVisit"]["duration"]["startTimestampMs"] = start_time
            data_unit["placeVisit"]["duration"]["endTimestampMs"] = end_time
            data_unit["placeVisit"]["location"]["address"] = places[start_location]["address"]
            data_unit["placeVisit"]["location"]["placeId"] = start_location   
            data_unit["placeVisit"]["location"]["name"] = places[start_location]["name"]    
            data_unit["placeVisit"]["location"]["latitudeE7"] = places[start_location]["latitude"]*1e7
            data_unit["placeVisit"]["location"]["longitudeE7"] = places[start_location]["longitude"]*1e7      

        if "activitySegment" in data_unit.keys():
            end_time = start_time + duration_activity
            data_unit["activitySegment"]["duration"]["startTimestampMs"] = start_time
            data_unit["activitySegment"]["duration"]["endTimestampMs"] = end_time
            data_unit["activitySegment"]['startLocation']['latitudeE7'] = places[start_location]["latitude"]*1e7
            data_unit["activitySegment"]['startLocation']['longitudeE7'] = places[start_location]["longitude"]*1e7           
            data_unit["activitySegment"]['endLocation']['latitudeE7'] = places[end_location]["latitude"]
            data_unit["activitySegment"]['endLocation']['longitudeE7'] = places[end_location]["latitude"]
            data_unit["activitySegment"]["duration"]["activityType"] = fake.random_element(elements=ACTIVITIES)
            start = (places[start_location]["latitude"], places[start_location]["longitude"])
            end = (places[end_location]["latitude"], places[end_location]["longitude"])
            data_unit["activitySegment"]["distance"] = geodesic(start, end).m

        start_time = end_time
        start_location = end_location
    
    return data


def fake_data(file_data):
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
    schema = get_faker_schema(json_schema["properties"], custom=SCHEMA_TYPES, iterations={"timelineObjects": NACTIVITIES})
    fake = Faker('nl_NL')
    fake.add_provider(geo)
    faker = FakerSchema(faker=fake, locale='nl_NL')
    data = faker.generate_fake(schema)
    data = update_data(data, datetime(2020, 1, 1))

    return data


if __name__ == '__main__':
    data = fake_data("test/data/Location History.zip")
    write_zipfile(data, "test.zip")

