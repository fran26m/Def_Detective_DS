import dataclasses
from typing import List, Tuple
from datetime import datetime, date, time

@dataclasses.dataclass
class Businesses:
    name: str
    email: str
    coordinates: Tuple[float, float]
    opening_hours: 'Business_hours'

@dataclasses.dataclass
class LostRequest:
    description: str
    email: str
    polygon: List[Tuple[float, float]]  # List of coordinates representing the polygon
    request_date: date
    lost_time: time

@dataclasses.dataclass
class Business_hours:
    opening_days: List[str]
    opening_time: time
    closing_time: time

def is_point_inside_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    x, y = point
    odd_nodes = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if yi < y and yj >= y or yj < y and yi >= y:
            if xi + (y - yi) / (yj - yi) * (xj - xi) < x:
                odd_nodes = not odd_nodes
        j = i
    return odd_nodes

def is_business_open_at_time(opening_hours: Business_hours, check_date: date, check_time: time) -> bool:
    return check_date.strftime('%A') in opening_hours.opening_days and opening_hours.opening_time <= check_time <= opening_hours.closing_time

def logic(data: List[Businesses], filter_condition: LostRequest) -> List[Businesses]:
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
                        coordinates=(52.5017, 13.4183),
                        opening_hours=Business_hours(opening_days=["Monday", "Tuesday"], opening_time=time(9, 0), closing_time=time(18, 0))
                    ),
                    Businesses(
                        email="qux@bar.zip",
                        name="qux",
                        coordinates=(52.4982, 13.4290),
                        opening_hours=Business_hours(opening_days=["Monday", "Wednesday"], opening_time=time(8, 30), closing_time=time(17, 30))
                    )
                ],
                "filter_condition": LostRequest(
                    description="I lost my wallet",
                    email="test@test.com",
                    polygon=[
                        (52.4980, 13.4170),  # Adjusting polygon coordinates to include 'foo' business
                        (52.5030, 13.4170),
                        (52.5030, 13.4200),
                        (52.4980, 13.4200)
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
