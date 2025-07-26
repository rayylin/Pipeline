import requests
from requests.auth import HTTPBasicAuth

# Replace with your real API key
api_key = 'YOUR_API_KEY'
company_number = '02723534'

url = f'https://find-and-update.company-information.service.gov.uk/company/04366849/officers' #https://api.company-information.service.gov.uk/company/{company_number}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
data = response.json()

print(data)