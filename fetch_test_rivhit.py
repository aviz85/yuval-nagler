import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

headers_rivhit = {
    'Content-Type': 'application/json'
}

rivhit_url = 'https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/Item.List'
rivhit_api_token = os.getenv('RIVHIT_API_TOKEN')
item_group_id = 1

payload = {
"api_token": rivhit_api_token,
"item_group_id": item_group_id
}
response = requests.post(rivhit_url, headers=headers_rivhit, data=json.dumps(payload))
response_data = response.json()
print(response_data)
if response.status_code != 200 or 'data' not in response_data:
    print(f"Error fetching data for item_group_id {item_group_id}: {response_data}")
    print(response)