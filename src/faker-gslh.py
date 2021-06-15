import json
import itertools
from datetime import datetime
from collections import OrderedDict
from calendar import monthrange

from zipfile import ZipFile
from genson import SchemaBuilder
from faker import Faker
from faker.providers import geo
from faker_schema.faker_schema import FakerSchema
from geopy.distance import geodesic

YEARS = [2019, 2020, 2021]
MONTHS = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
]

# Different behaviour per year
NPLACES = {2019: 50, 2020: 50, 2021: 20}
NACTIVITIES = {2019: 500, 2020: 500, 2021: 250}
TOP_PLACES = {2019: [0.4, 0.3, 0.05], 2020: [0.4, 0.3, 0.05], 2021: [0.8, 0.03, 0.02]}
ACTIVITIES = {
    2019: OrderedDict({
        "CYCLING": 0.3,
        "WALKING": 0.2,
        "IN_VEHICLE": 0.3,
        "IN_TRAIN": 0.2
    }),
    2020: OrderedDict({
        "CYCLING": 0.3,
        "WALKING": 0.2,
        "IN_VEHICLE": 0.3,
        "IN_TRAIN": 0.2
    }),
    2021: OrderedDict({
        "CYCLING": 0.4,
        "WALKING": 0.5,
        "IN_VEHICLE": 0.1
    }),
}
FRACTION_PLACES = {2019: 0.8, 2020: 0.8, 2021: 0.95}

# schema with types
SCHEMA_TYPES = {
    'name': 'company',
    'visitConfidence': 'random_digit_not_null',
    'accuracyMeters': 'random_digit_not_null'
}


def get_faker_schema(json_schema, custom=None, iterations={}, parent_key=None):
    if "type" not in json_schema:
        key = next(iter(json_schema))
        if isinstance(custom, dict) and key in custom:
            value = custom[key]
        else:
            value = get_faker_schema(
                json_schema[key], custom=custom, iterations=iterations, parent_key=key)
        return {key: value}
    elif json_schema['type'] == "object":
        value = {}
        for prop, val in json_schema["properties"].items():
            value.update(get_faker_schema({prop: val}, custom=custom, iterations=iterations))
    elif json_schema['type'] == "array":
        iters = iterations.get(parent_key, 1)
        value = [get_faker_schema(
            json_schema['items'], custom=custom, iterations=iterations) for i in range(iters)]
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
        latitude = fake.unique.coordinate(center=latlon[0], radius=0.05)
        longitude = fake.unique.coordinate(center=latlon[1], radius=0.05)
        place = {
            "name": fake.unique.company(),
            "address": fake.unique.address(),
            "latitude": float(latitude),
            "longitude": float(longitude)
        }
        places.update({fake.unique.pystr_format(): place})
    return places


def update_data(data, start_date, places, seed=None):

    start_time = start_date.timestamp() * 1.e3
    year = start_date.year
    ndays = monthrange(year, start_date.month)[1]
    duration = ndays * 24 * 60 * 60 * 1.e3 / NACTIVITIES[year]
    duration_place = FRACTION_PLACES[year] * duration
    duration_activity = (1.0 - FRACTION_PLACES[year]) * duration

    elements = OrderedDict()
    for number, place in enumerate(places):
        if number < len(TOP_PLACES[year]):
            elements[place] = TOP_PLACES[year][number]
        else:
            elements[place] = (1.0 - sum(TOP_PLACES[year]))/(NPLACES[year] - len(TOP_PLACES[year]))

    fake = Faker()
    if seed is not None:
        fake.seed_instance(seed)
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
            data_unit["placeVisit"]["location"]["latitudeE7"] = places[
                start_location]["latitude"]*1e7
            data_unit["placeVisit"]["location"]["longitudeE7"] = places[
                start_location]["longitude"]*1e7
            start_time = end_time

        if "activitySegment" in data_unit:
            end_time = start_time + duration_activity
            data_unit["activitySegment"]["duration"]["startTimestampMs"] = start_time
            data_unit["activitySegment"]["duration"]["endTimestampMs"] = end_time
            data_unit["activitySegment"]['startLocation']['latitudeE7'] = places[
                start_location]["latitude"]*1e7
            data_unit["activitySegment"]['startLocation']['longitudeE7'] = places[
                start_location]["longitude"]*1e7
            data_unit["activitySegment"]['endLocation']['latitudeE7'] = places[
                end_location]["latitude"]
            data_unit["activitySegment"]['endLocation']['longitudeE7'] = places[
                end_location]["latitude"]
            data_unit["activitySegment"]["duration"]["activityType"] = fake.random_element(
                elements=ACTIVITIES[year])
            start = (places[start_location]["latitude"], places[start_location]["longitude"])
            end = (places[end_location]["latitude"], places[end_location]["longitude"])
            data_unit["activitySegment"]["distance"] = geodesic(start, end).m
            start_time = end_time

        start_location = end_location
    # print("end", datetime.fromtimestamp(end_time/1e3))

    return data


def write_zipfile(data, zipfile):
    """

    """
    with ZipFile(zipfile, 'w') as zip_archive:
        for year, month in data:
            with zip_archive.open(
                'Takeout/Location History/Semantic Location History/' +
                str(year) + '/' + str(year) + '_' + month + '.json', 'w'
            ) as file1:
                file1.write(
                    json.dumps(data[(year, month)]).encode('utf-8')
                )


def fake_data(json_file):
    """Return faked json data
    Args:
        json_file: example json file with data to simulate

    Returns:
        dict: dict with summary and DataFrame with extracted data
    """

    # get dict of visited places
    places = create_places(total=max(NPLACES.values()))

    builder = SchemaBuilder()
    with open(json_file) as f:
        data = json.load(f)
    builder.add_object(data)
    json_schema = builder.to_schema()

    fake = Faker('nl_NL')
    fake.add_provider(geo)
    faker = FakerSchema(faker=fake, locale='nl_NL')

    fake_data = {}
    seed = 0
    for year in YEARS:
        for month in MONTHS:
            schema = get_faker_schema(
                json_schema["properties"],
                custom=SCHEMA_TYPES,
                iterations={"timelineObjects": NACTIVITIES[year]})

            data = faker.generate_fake(schema)
            month_number = datetime.strptime(month[:3], '%b').month
            seed += 1
            fake_data[(year, month)] = update_data(
                data, datetime(year, month_number, 1),
                dict(itertools.islice(places.items(), NPLACES[year])),
                seed=seed
            )

    write_zipfile(fake_data, "Location History.zip")
    return data


if __name__ == '__main__':
    data = fake_data("test/data/2020_JANUARY.json")
