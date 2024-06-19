import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

rivhit_api_token = os.getenv('RIVHIT_API_TOKEN')
monday_api_token = os.getenv('MONDAY_API_TOKEN')
monday_board_id = '1505150501'

rivhit_url = 'https://api.rivhit.co.il/online/RivhitOnlineAPI.svc/Item.List'
monday_url = 'https://api.monday.com/v2'

headers_rivhit = {
    'Content-Type': 'application/json'
}

headers_monday = {
    'Content-Type': 'application/json',
    'Authorization': monday_api_token
}

def insert_to_monday(data):
    query = 'mutation ($boardId: ID! , $itemName: String! , $colVals: JSON!) { create_item (board_id:$boardId, item_name:$itemName, column_values:$colVals) { id } }'
    
    try:
        column_values = json.dumps({
            "numbers__1": data.get('item_id'),  # מק"ט
            "numbers4__1": {'string': data.get('barcode')},
            "numbers3__1": data.get('cost_nis'),
            "numbers6__1": data.get('sale_nis'),    
        })
    except (TypeError, ValueError) as e:
        print(f"Error serializing column_values: {e}")
        return None
    print(column_values)
    variables = {
        "boardId": monday_board_id,
        "itemName": data.get('name', ''),
        "colVals": column_values
    }
    data = {
        'query' : query, 'variables' : variables
    }
    
    # Debug: print query and variables
    print("Query:")
    print(query)
    print("Variables:")
    print(json.dumps(variables, indent=2))
    
    response = requests.post(monday_url, headers=headers_monday, json={'query': query, 'variables': variables})
    
    # Print the response status code and text for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code != 200:
        print(f"Error inserting data into Monday.com: {response.json()}")
        return None
    
    return response.json()

# Example usage
data = {
    "item_id": 42,
    "name": "טי.פי.אי שחור (לירון) מידה S - (100 יח) - ללא אבקה",
    "item_extended_description": "כפפות טי.פי.אי - צבע שחור - 100 יח' בקופסא - כשרות חתם סופר - מתאים לעבודה עם מזון - ללא אבקה",
    "item_part_num": "6906539758136",
    "barcode": "6906539758136",
    "item_group_id": 1,
    "storage_id": 1,
    "quantity": 130.0,
    "cost_nis": 4.76,
    "sale_nis": 8.0,
    "currency_id": 1,
    "cost_mtc": 0.0,
    "sale_mtc": 0.0,
    "picture_link": "https://api.rivhit.co.il/online/FileService.svc/getItemPic/315071829/faffkj1v",
    "exempt_vat": False,
    "avitem": 0,
    "location": None,
    "is_serial": 0,
    "sapak": 0,
    "item_name_en": ''
}
insert_to_monday(data)

# Example from which we are learning
apiKey = "YOUR_API_KEY_HERE"
apiUrl = "https://api.monday.com/v2"
headers = {"Authorization" : apiKey}

query4 = 'mutation ($myItemName: String!) { create_item (board_id:YOUR_BOARD_ID, item_name:$myItemName) { id } }'
vars = {'myItemName' : 'Hello everyone!'}
data = {'query' : query4, 'variables' : vars}

r = requests.post(url=apiUrl, json=data, headers=headers) # make request
print(r.json())
