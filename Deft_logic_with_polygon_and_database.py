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
    opening_hours: 'Business_hours'

@dataclasses.dataclass
class LostRequest:
    description: str
    email: str
    polygon: List[Point]
    request_date: date
    lost_time: time

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

def logic(data: List[Businesses], filter_condition: LostRequest, geojson_file_path: str) -> List[Businesses]:
    # Load the GeoJSON file as a GeoDataFrame
    gdf = gpd.read_file(geojson_file_path)
    
    filtered_businesses = []
    for _, row in gdf.iterrows():
        business = Businesses(
            name=row['name'],
            email=row['email'],
            coordinates=Point(row['geometry'].x, row['geometry'].y),
            opening_hours=Business_hours(
                opening_days=row['opening_days'].split(', '),
                opening_time=time.fromisoformat(row['opening_time']),
                closing_time=time.fromisoformat(row['closing_time'])
            )
        )
        if (is_point_inside_polygon(business.coordinates, filter_condition.polygon) and 
            is_business_open_at_time(business.opening_hours, filter_condition.request_date, filter_condition.lost_time)):
            filtered_businesses.append(business)
    return filtered_businesses

def test_logic():
    tests = [
        {
            "input": {
                "data": [],
                "filter_condition": LostRequest(
                    description="I lost my wallet",
                    email="test@test.com",
                    polygon=[
                        Point(52.4980, 13.4170),  # Adjusting polygon coordinates to include 'foo' business
                        Point(52.5030, 13.4170),
                        Point(52.5030, 13.4200),
                        Point(52.4980, 13.4200)
                    ],
                    request_date=date(2023, 8, 21),  # Monday 21/08/2023
                    lost_time=time(10,0)
