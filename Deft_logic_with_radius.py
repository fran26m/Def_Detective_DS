import dataclasses
from typing import List, Tuple
from datetime import datetime, time, date
import math

@dataclasses.dataclass
class Businesses:
    name: str
    email: str
    coordinates: Tuple[float, float] #lat, long
    opening_hours: 'Business_hours'

@dataclasses.dataclass
class LostRequest:
    description: str
    email: str
    location_coordinates: Tuple[float,float]
    radius: float
    request_date: date
    lost_time: time

@dataclasses.dataclass
class Business_hours:
    opening_days: List[str]
    opening_time: time
    closing_time: time

def haversine_distance(coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
    R = 6371000
    lat1, lon1 = math.radians(coords1[0]), math.radians(coords1[1])
    lat2, lon2 = math.radians(coords2[0]), math.radians(coords2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_business_open_at_time(opening_hours: Business_hours, check_date: date, check_time: time) -> bool:
    day_of_week = check_date.strftime('%A')
    is_open_on_day = day_of_week in opening_hours.opening_days
    is_within_opening_hours = opening_hours.opening_time <= check_time <= opening_hours.closing_time
    #print(f"Business is open on {day_of_week}: {is_open_on_day}. Open hours: {opening_hours.opening_time} - {opening_hours.closing_time}. Lost time: {check_time}. Within opening hours: {is_within_opening_hours}.")

    return is_open_on_day and is_within_opening_hours

def logic(data: List[Businesses], filter_condition: LostRequest) -> List[Businesses]:
    filtered_businesses = []
    for business in data:
        distance = haversine_distance(business.coordinates, filter_condition.location_coordinates)
        #print(f"Distance from {business.name}: {distance} meters")

        if (distance <= filter_condition.radius and 
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
                        coordinates=(52.5017, 13.4183),
                        opening_hours=Business_hours(opening_days=["Monday", "Tuesday"], opening_time=time(9, 0), closing_time=time(18, 0))
                    ),
                    Businesses(
                        email="qux@bar.zip",
                        name="qux",
                        coordinates=(52.4982, 13.4290),
                        opening_hours=Business_hours(opening_days=["Monday", "Wednesday"], opening_time=time(18, 30), closing_time=time(23, 30))
                    )
                ],
                "filter_condition": LostRequest(
                    description="I lost my wallet",
                    email="test@test.com",
                    location_coordinates=(52.4990, 13.4267),
                    radius=700.0,
                    request_date=date(2023, 8, 21),
                    lost_time=time(10, 0)
                ),
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
