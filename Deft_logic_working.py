import geopandas as gpd
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
    #opening_hours: 'Business_hours'

@dataclasses.dataclass
class LostRequest:
    description: str
    email: str
    polygon: List[Point]

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

def logic(data: List[Businesses], filter_condition: LostRequest, geojson_file_path: str) -> List[Businesses]:
    # Load the GeoJSON file as a GeoDataFrame
    gdf = gpd.read_file("https://raw.githubusercontent.com/TechLabs-Berlin/ss23-deft-detective/8b9eab4335837c2aec83fc79684261938888d2a2/data/places.geojson")

    filtered_businesses = []
    for _, row in gdf.iterrows():
      if row['geometry'].geom_type == 'Point':
        business = Businesses(
            name=row['name'],
            email=row['email'],
            coordinates=Point(row['geometry'].x, row['geometry'].y)  #change 3
        )

        if is_point_inside_polygon(business.coordinates, filter_condition.polygon):
            filtered_businesses.append(business)
    return filtered_businesses

def test_specific_point():
    geojson_file_path = "https://raw.githubusercontent.com/TechLabs-Berlin/ss23-deft-detective/8b9eab4335837c2aec83fc79684261938888d2a2/data/places.geojson"
    filter_condition = LostRequest(
        description="Test specific point",
        email="test@test.com",
        polygon=[
            Point(13.402, 52.533),
            Point(13.4025, 52.533),
            Point(13.4025, 52.5335),
            Point(13.402, 52.5335)
            ]
        )
    filtered_businesses = logic([], filter_condition, geojson_file_path)
    print("Filtered Businesses:")
    for business in filtered_businesses:
        print(f"Name: {business.name}, Email: {business.email}, Coordinates: ({business.coordinates.lon}, {business.coordinates.lat})")

# Run the test for a specific point
test_specific_point()