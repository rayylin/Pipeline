import requests


url = "https://data.cr.gov.hk/cr/api/api/v1/api_builder/json/local/search"

# Define the query parameters
params = {
    "query[0][key1]": "Comp_name",
    "query[0][key2]": "begins_with",
    "query[0][key3]": "HSBC Digital Technology Holding Group Co., Limited"
}

# Make the GET request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")