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

# Function to fetch data from Rivhit
def fetch_rivhit_data(item_group_id):
    payload = {
        "api_token": rivhit_api_token,
        "item_group_id": item_group_id
    }
    response = requests.post(rivhit_url, headers=headers_rivhit, data=json.dumps(payload))
    response_data = response.json()
    if response.status_code != 200 or 'data' not in response_data:
        print(f"Error fetching data for item_group_id {item_group_id}: {response_data}")
        return []
    return response_data['data']['item_list']

# Function to transform Rivhit data to Monday.com schema
def transform_to_monday_schema(item):
    return {
        "item_id": item.get('item_id', ''),
        "name": item.get('item_name', ''),
        "person": "",  # Placeholder, adjust as necessary
        "status": "",  # Placeholder, adjust as necessary
        "numbers__1": item.get('item_id', 0),
        "numbers4__1": item.get('barcode', 0),
        "dropdown__1": "",  # Placeholder, adjust as necessary
        "numbers3__1": item.get('cost_nis', 0.0),
        "numbers6__1": item.get('sale_nis', 0.0),
        "dropdown7__1": item.get('item_group_id', ''),
        "dropdown8__1": "",  # Placeholder, adjust as necessary
        "numbers5__1": item.get('storage_id', 0),
        "numbers49__1": item.get('cost_mtc', 0.0),
        "numbers65__1": item.get('sale_mtc', 0.0),
        "files__1": item.get('picture_link', ''),
        "numbers7__1": 0,  # Placeholder, adjust as necessary
        "numbers653__1": 0,  # Placeholder, adjust as necessary
        "numbers9__1": 0,  # Placeholder, adjust as necessary
        "long_text__1": item.get('item_extended_description', ''),
        "numbers8__1": 0,  # Placeholder, adjust as necessary
        "numbers63__1": 0,  # Placeholder, adjust as necessary
        "numbers42__1": 0,  # Placeholder, adjust as necessary
        "numbers1__1": 0,  # Placeholder, adjust as necessary
        "numbers31__1": item.get('quantity', 0)
    }

# Function to insert data into Monday.com
def insert_to_monday(data):
    query = '''
    mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
        create_item (board_id: $board_id, item_name: $item_name, column_values: $column_values) {
            id
        }
    }
    '''
    try:
        column_values = json.dumps(data)
    except (TypeError, ValueError) as e:
        print(f"Error serializing column_values: {e}")
        return None

    variables = {
        "board_id": monday_board_id,
        "item_name": data.get('name', ''),
        "column_values": column_values
    }
    
    # Debug: print query and variables
    print("Query:")
    print(query)
    print("Variables:")
    print(json.dumps(variables, indent=2))
    
    response = requests.post(monday_url, headers=headers_monday, json={'query': query, 'variables': variables})
    
    if response.status_code != 200:
        print(f"Error inserting data into Monday.com: {response.json()}")
        return None
    
    return response.json()
    
# Main script to fetch, transform, and insert data
def main():

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
    for item_group_id in range(1, 2):
        rivhit_data = fetch_rivhit_data(item_group_id)
        print(f"Fetched data for item_group_id {item_group_id}: {rivhit_data}")
        for item in rivhit_data:
            try:
                print(f"Processing item: {item}")
                transformed_data = transform_to_monday_schema(item)
                insert_result = insert_to_monday(transformed_data)
                print(insert_result)
            except Exception as e:
                print(f"Error processing item {item}: {e}")

if __name__ == "__main__":
    main()
