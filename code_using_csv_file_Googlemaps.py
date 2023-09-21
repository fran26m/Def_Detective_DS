from google.colab import drive
drive.mount('/content/drive')

! pip install flask_ngrok

import pandas as pd
df = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/Deft_detective/berlin_places_2000_with_details.csv')   ### ###this, stoerd in google drive, shared with francisco
#print(df.head())
duplicate_names_before = df.duplicated(subset=['Name'], keep=False).sum()
print(f"There are {duplicate_names_before} duplicate names in the DataFrame before removal.")

# Remove rows with duplicate names, keeping only the first occurrence
df.drop_duplicates(subset=['Name'], keep='first', inplace=True)

# Find and count duplicate names after removal
duplicate_names_after = df.duplicated(subset=['Name'], keep=False).sum()
print(f"There are {duplicate_names_after} duplicate names in the DataFrame after removal.")

# Save the cleaned DataFrame back to a new CSV file to use
df.to_csv('cleaned_file.csv', index=False)          #this file, the cleaned data file "creates itself" every time in this directory so it can then be used below

df.head()

######################################################################################################################################################
#################################################################################################################################################

## attempt to build on previous...not even close yet


from flask import Flask, request, jsonify
import pandas as pd
from typing import List, Dict

# Initialize Flask app
app = Flask(__name__)




class Point:
    def __init__(self, lat: float, lon: float):
        if lat < -90 or lat > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if lon <= -180 or lon > 180:
            raise ValueError("Longitude must be between -179.9999 and 180 degrees")

        self.lat = lat
        self.lon = lon

def is_point_inside_polygon(point: Point, polygon: List[Point]) -> bool:
    x, y = point.lat, point.lon
    odd_nodes = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i].lat, polygon[i].lon
        xj, yj = polygon[j].lat, polygon[j].lon
        if xi < x and xj >= x or xj < x and xi >= x:
            if yi + (x - xi) / (xj - xi) * (yj - yi) < y:
                odd_nodes = not odd_nodes
        j = i
    return odd_nodes

def filter_businesses(csv_file_path: str, polygon: List[Point]) -> List[Dict[str, str]]:
    df = pd.read_csv(csv_file_path)
    filtered_business_info = []

    for _, row in df.iterrows():
        point = Point(row['Latitude'], row['Longitude'])
        if is_point_inside_polygon(point, polygon):
            business_info = {
                'Name': row['Name'],
                'Address': row['Address'],
                'Phone number': row['Phone Number']

            }
            filtered_business_info.append(business_info)

    # Create a new DataFrame from the filtered business information
    filtered_df = pd.DataFrame(filtered_business_info)

    # Save the new DataFrame to a CSV file
    filtered_df.to_csv('filtered_businesses.csv', index=False)

    # Save the filtered business information to a JSON file
    json_str = filtered_df.to_json(orient='records')
    with open('filtered_businesses.json', 'w') as f:
      f.write(json_str)

    #print them out here so I check they are in the right place
    return filtered_business_info


# Default perimeter
default_perimeter = [
    Point(52.4980, 13.4170),
    Point(52.5030, 13.4170),
    Point(52.5030, 13.4200),
    Point(52.4980, 13.4200),
]

# Path to your CSV file
csv_file_path = "/content/cleaned_file.csv"

@app.route('/filter_businesses', methods=['POST'])     # I suppose this is where it is missing the path (route) to the api. But why doesn't it work given the "except" afterwards?
def api_filter_businesses():
    try:
        # Try to get JSON payload from request
        payload = request.json

        # Validate payload and create perimeter
        perimeter = [Point(coord['lat'], coord['lon']) for coord in payload['perimeter']]
    except:
        # Use default perimeter if payload is invalid or doesn't exist
        perimeter = default_perimeter

    # Call filter_businesses and return as JSON
    filtered_business_info = filter_businesses(csv_file_path, perimeter)
    return jsonify(filtered_business_info)

if __name__ == '__main__':
    app.run(debug=True)

###############################################################################################################################################
###################################################################################################################################################

# The next two scripts are very slight variations of the same. This is still missing the flask calling (being called?  conceptual doubt) the API

import pandas as pd
import requests
from typing import List, Dict, Optional

class Point:
    def __init__(self, lat: float, lon: float):
        if lat < -90 or lat > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if lon <= -180 or lon > 180:
            raise ValueError("Longitude must be between -179.9999 and 180 degrees")

        self.lat = lat
        self.lon = lon

def is_point_inside_polygon(point: Point, polygon: List[Point]) -> bool:
    x, y = point.lat, point.lon
    odd_nodes = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i].lat, polygon[i].lon
        xj, yj = polygon[j].lat, polygon[j].lon
        if xi < x and xj >= x or xj < x and xi >= x:
            if yi + (x - xi) / (xj - xi) * (yj - yi) < y:
                odd_nodes = not odd_nodes
        j = i
    return odd_nodes

def fetch_perimeter_from_api(api_url: str) -> List[Point]:
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from API")

    data = response.json()
    return [Point(lat, lon) for lat, lon in data['perimeter']]

def filter_businesses(csv_file_path: str, api_url: Optional[str] = None) -> None:
    # Fetch perimeter from API if available, otherwise use manual input
    if api_url:
        perimeter = fetch_perimeter_from_api(api_url)
    else:
        # Manually defined perimeter (use this if API is not available)
        perimeter = [
            Point(52.4980, 13.4170),  # small area in kreuzberg
            Point(52.5030, 13.4170),
            Point(52.5030, 13.4200),
            Point(52.4980, 13.4200),
        ]
    #df = pd.read_csv(csv_file_path)    # completely unnecessary?

    filtered_business_info = []

    for _, row in df.iterrows():
        point = Point(row['Latitude'], row['Longitude'])
        if is_point_inside_polygon(point, perimeter):
            business_info = {
                'Name': row['Name'],
                'Address': row['Address'],
                'Phone Number:': row['Phone Number']
            }
            filtered_business_info.append(business_info)

    # Create a new DataFrame from the filtered business information
    filtered_df = pd.DataFrame(filtered_business_info)

    # Save the new DataFrame to a CSV file
    filtered_df.to_csv('filtered_businesses.csv', index=False)
    return filtered_business_info
    #print(filtered_df.to_csv)    #<-- doesn't seem to actually do anything?



# Path to your CSV file
csv_file_path = '/content/cleaned_file.csv'

# API URL to fetch the perimeter (replace with your actual API URL)
# api_url = 'http://example.com/api/getPerimeter'

# Filter businesses and save the result to a CSV file
filter_businesses(csv_file_path)     #if api is there, this would need a second argument api_url ?

#####################################################################################################################
########################################################################################################################

# this one looks cleaner?

import pandas as pd
from typing import List, Dict
import json

class Point:
    def __init__(self, lat: float, lon: float):
        if lat < -90 or lat > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if lon <= -180 or lon > 180:
            raise ValueError("Longitude must be between -179.9999 and 180 degrees")

        self.lat = lat
        self.lon = lon

def is_point_inside_polygon(point: Point, polygon: List[Point]) -> bool:
    x, y = point.lat, point.lon
    odd_nodes = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i].lat, polygon[i].lon
        xj, yj = polygon[j].lat, polygon[j].lon
        if xi < x and xj >= x or xj < x and xi >= x:
            if yi + (x - xi) / (xj - xi) * (yj - yi) < y:
                odd_nodes = not odd_nodes
        j = i
    return odd_nodes

def filter_businesses(csv_file_path: str, polygon: List[Point]) -> List[Dict[str, str]]:
    df = pd.read_csv(csv_file_path)
    filtered_business_info = []

    for _, row in df.iterrows():
        point = Point(row['Latitude'], row['Longitude'])
        if is_point_inside_polygon(point, polygon):
            business_info = {
                'Name': row['Name'],
                'Address': row['Address'],
                'Phone number': row['Phone Number']

            }
            filtered_business_info.append(business_info)

    # Create a new DataFrame from the filtered business information
    filtered_df = pd.DataFrame(filtered_business_info)

    # Save the new DataFrame to a CSV file
    filtered_df.to_csv('filtered_businesses.csv', index=False)

    # Save the filtered business information to a JSON file
    json_str = filtered_df.to_json(orient='records')
    with open('filtered_businesses.json', 'w') as f:
      f.write(json_str)

    #print them out here so I check they are in the right place
    return filtered_business_info

# Define the perimeter as a list of Point objects


perimeter = [
    Point(52.4980, 13.4170),  # small area in kreuzberg
    Point(52.5030, 13.4170),
    Point(52.5030, 13.4200),
    Point(52.4980, 13.4200),
   # Point(52.7130, 13.4270),
   # Point(52.7130, 13.5270)   #added a semi random, quite far away 5th and 6th points, would great to be able to visualise this, i think its essentially a narrow, long, strip
]

# Path to your CSV file
csv_file_path = "/content/cleaned_file.csv"

# Get businesses inside the perimeter
filtered_business_info = filter_businesses(csv_file_path, perimeter)

# Print the filtered business information
for business in filtered_business_info:
    print(f"Name: {business['Name']}, Address: {business['Address']},Phone number: {business['Phone number']} ")

####################################################################################################################################333
#######################################################################################################################################

# first crack at "flasking" this


from flask import Flask, request, jsonify
import pandas as pd
from typing import List, Dict
import json                   #apparently no longer needed, as flask does the whole turning into JSON thing? will need to remove the bit where I converted to JSON below as well.

class Point:
    def __init__(self, lat: float, lon: float):
        if lat < -90 or lat > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if lon <= -180 or lon > 180:
            raise ValueError("Longitude must be between -179.9999 and 180 degrees")

        self.lat = lat
        self.lon = lon

def is_point_inside_polygon(point: Point, polygon: List[Point]) -> bool:
    x, y = point.lat, point.lon
    odd_nodes = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i].lat, polygon[i].lon
        xj, yj = polygon[j].lat, polygon[j].lon
        if xi < x and xj >= x or xj < x and xi >= x:
            if yi + (x - xi) / (xj - xi) * (yj - yi) < y:
                odd_nodes = not odd_nodes
        j = i
    return odd_nodes

def filter_businesses(csv_file_path: str, polygon: List[Point]) -> List[Dict[str, str]]:
    df = pd.read_csv(csv_file_path)
    filtered_business_info = []

    for _, row in df.iterrows():
        point = Point(row['Latitude'], row['Longitude'])
        if is_point_inside_polygon(point, polygon):
            business_info = {
                'Name': row['Name'],
                'Address': row['Address'],
                'Phone number': row['Phone Number']

            }
            filtered_business_info.append(business_info)

    # Create a new DataFrame from the filtered business information
    filtered_df = pd.DataFrame(filtered_business_info)

    # Save the new DataFrame to a CSV file
    filtered_df.to_csv('filtered_businesses.csv', index=False)

    # Save the filtered business information to a JSON file
    json_str = filtered_df.to_json(orient='records')
    with open('filtered_businesses.json', 'w') as f:
      f.write(json_str)

    #print them out here so I check they are in the right place
    return filtered_business_info


# Define the perimeter as a list of Point objects


perimeter = [
    Point(52.4980, 13.4170),  # small area in kreuzberg
    Point(52.5030, 13.4170),
    Point(52.5030, 13.4200),
    Point(52.4980, 13.4200),
   # Point(52.7130, 13.4270),
   # Point(52.7130, 13.5270)   #added a semi random, quite far away 5th and 6th points, would great to be able to visualise this, i think its essentially a narrow, long, strip
]

# Path to your CSV file
csv_file_path = "/content/cleaned_file.csv"

# Get businesses inside the perimeter
filtered_business_info = filter_businesses(csv_file_path, perimeter)

# Print the filtered business information
for business in filtered_business_info:
    print(f"Name: {business['Name']}, Address: {business['Address']},Phone number: {business['Phone number']} ")

###########################################################################################################################33
###########################################################################################################################3
