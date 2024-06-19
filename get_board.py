import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_url = "https://api.monday.com/v2"
api_key = os.getenv("MONDAY_API_TOKEN")

headers = {
    "Authorization": api_key
}

query = """
{
  boards(ids: 1505150501) {
    columns {
      id
      title
    }
  }
}
"""

response = requests.post(api_url, headers=headers, json={'query': query})

if response.status_code == 200:
    data = response.json()
    columns = data['data']['boards'][0]['columns']
    for column in columns:
        print(f"ID: {column['id']}, Title: {column['title']}")
else:
    print(f"Failed to fetch data: {response.status_code}")
