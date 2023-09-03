import geopandas as gpd # pip install geopandas
import dataclasses
from typing import List, Tuple
from datetime import datetime, date, time


class Point:
    def __init__(self, lon: float, lat: float):
        if lon <= -180 or lon >= 180:
            raise ValueError("longitude must be between -179 and 180 degrees")
        if lat < -90 or lat > 90:
            raise ValueError("latitude must be between -90 and 90 degrees")
        
        self.lon = lon
        self.lat = lat

    def __eq__(self, other: "Point") -> bool:
        return self.lon == other.lon and self.lat == other.lat

@dataclasses.dataclass
class Businesses:
    name: str
    email: str
    coordinates: Point
    opening_hours: 'Business_hours'

@dataclasses.dataclass
class LostRequest:
    description: str
    email: str
    polygon: List[Point]  # List of coordinates representing the polygon
    request_date: date
    lost_time: time

@dataclasses.dataclass
class Business_hours:
    opening_days: List[str]
    opening_time: time
    closing_time: time

def is_point_inside_polygon(point: Point, polygon: List[Point]) -> bool:
    x, y = point.lon, point.lat
    odd_nodes = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i].lon, polygon[i].lat
        xj, yj = polygon[j].lon, polygon[j].lat
        if yi < y and yj >= y or yj < y and yi >= y:
            if xi + (y - yi) / (yj - yi) * (xj - xi) < x:
                odd_nodes = not odd_nodes
        j = i
    return odd_nodes

def is_business_open_at_time(opening_hours: Business_hours, check_date: date, check_time: time) -> bool:
    return check_date.strftime('%A') in opening_hours.opening_days and opening_hours.opening_time <= check_time <= opening_hours.closing_time

#Q 1: How do we get the data from the database?
#Q 2: How do we get the polygon coordinates from the frontend? -- for later?
#Q 3: where does gdf get used?

def logic(data: List[Businesses], filter_condition: LostRequest, geojson_file_path: str) -> List[Businesses]:   '''list[Businesses] has to be drawn 
    from the database'''
    # Load the GeoJSON file as a GeoDataFrame
    gdf = gpd.read_file("https://github.com/TechLabs-Berlin/ss23-deft-detective/blob/8b9eab4335837c2aec83fc79684261938888d2a2/data/places.geojson")
    filtered_businesses = []
    for business in data:
        if (is_point_inside_polygon(business.coordinates, filter_condition.polygon) and 
            is_business_open_at_time(business.opening_hours, filter_condition.request_date, filter_condition.lost_time)):
            filtered_businesses.append(business)
    return filtered_businesses

def test_logic():
    tests = [
        {
            "input": {
                "data": [
                    Businesses(
                        email="foo@bar.zip",
                        name="foo",
                        coordinates=Point(52.5017, 13.4183),
                        opening_hours=Business_hours(opening_days=["Monday", "Tuesday"], opening_time=time(9, 0), closing_time=time(18, 0))
                    ),
                    Businesses(
                        email="qux@bar.zip",
                        name="qux",
                        coordinates=Point(52.4982, 13.4290),
                        opening_hours=Business_hours(opening_days=["Monday", "Wednesday"], opening_time=time(8, 30), closing_time=time(17, 30))
                    )
                ],
                "filter_condition": LostRequest(
                    description="I lost my wallet",
                    email="test@test.com",
                    polygon=[
                        Point(52.4980, 13.4170),  # Adjusting polygon coordinates to include 'foo' business
                        Point(52.5030, 13.4170),
                        Point(52.5030, 13.4200),
                        Point(52.4980, 13.4200)
                    ],
                    request_date=date(2023, 8, 21), #monday 21/08/2023
                    lost_time=time(10, 0)
                )
            },
            "want": [
                Businesses(
                    email="foo@bar.zip",
                    name="foo",
                    coordinates=(52.5017, 13.4183),
                    opening_hours=Business_hours(opening_days=["Monday", "Tuesday"], opening_time=time(9, 0), closing_time=time(18, 0))
                )
            ]
        }
    ]

    for i, test in enumerate(tests, 1):
        got = logic(test["input"]["data"], test["input"]["filter_condition"])
        if got == test["want"]:
            print(f"Test {i} passed!")
        else:
            print(f"Test {i} failed. Expected: {test['want']}, but got: {got}")

test_logic()
