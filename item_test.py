import requests
import json
from dotenv import load_dotenv
import os
import re

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
    'Authorization': monday_api_token,
    'API-Version': '2023-10'  # Specify API version
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

# Function to generate dummy data for testing
def generate_dummy_data():
    return [{
        "item_id": 42,
        "name": "Test Item",
        "barcode": "1234567890123",
        "sapak": 1,
        "cost_nis": 10.5,
        "sale_nis": 20.0,
        "item_group_id": 1,
        "storage_id": 1,
        "quantity": 100,
        "cost_mtc": 2.5,
        "sale_mtc": 5.0,
        "picture_link": "https://example.com/image.jpg",
        "item_extended_description": "This is a test item with an extended description."
    }]

def clean_string(s, max_length=255):
    # Remove special characters and limit length
    if s is None:
        return ''
    cleaned = re.sub(r'[^\w\s-]', '', str(s))
    return cleaned[:max_length]

# Define the conversion array for sapak
SAPAK_CONVERSION = [0, 499, 674, 677]

def transform_to_monday_schema(item):
    name = clean_string(item.get('item_name', '').strip())
    if not name:
        name = clean_string(item.get('item_extended_description', '').strip())
        if not name:
            name = f"Item {item.get('item_id', 'Unknown')}"

    picture_link = os.path.basename(item.get('picture_link', '')) if item.get('picture_link') else ''

    # Safe conversion for numeric fields
    def safe_float(value, default=0.0):
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    # Convert sapak value
    sapak_value = item.get('sapak', 0)
    converted_sapak = str(SAPAK_CONVERSION.index(sapak_value)) if sapak_value in SAPAK_CONVERSION else '0'

    return {
        "name": name,
        "numbers__1": safe_float(item.get('item_id')),
        "text__1": clean_string(item.get('barcode', '')),
        "dropdown__1": converted_sapak,  # Use the converted sapak value
        "numbers3__1": round(safe_float(item.get('cost_nis')), 2),
        "numbers6__1": round(safe_float(item.get('sale_nis')), 2),
        "dropdown7__1": str(item.get('item_group_id', '')),
        "dropdown8__1": str(item.get('storage_id', '')),
        "numbers5__1": round(safe_float(item.get('quantity')), 2),
        "numbers49__1": round(safe_float(item.get('cost_mtc')), 2),
        "numbers65__1": round(safe_float(item.get('sale_mtc')), 2),
        "long_text__1": clean_string(item.get('item_extended_description', ''), 2000),
        "numbers31__1": round(safe_float(item.get('quantity')), 2)
    }
        
def insert_to_monday(data):
    query = '''
    mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
        create_item (board_id: $board_id, item_name: $item_name, column_values: $column_values) {
            id
        }
    }
    '''
    
    # Ensure item_name is not empty
    item_name = data.get('name', '').strip()
    if not item_name:
        print("Error: item_name is empty. Skipping this item.")
        return None

    try:
        column_values = json.dumps(data)
        print(f"Column values: {column_values}")
    except (TypeError, ValueError) as e:
        print(f"Error serializing column_values: {e}")
        return None
    
    variables = {
        "board_id": monday_board_id,
        "item_name": item_name,
        "column_values": column_values
    }
    
    print("Query:")
    print(query)
    print("Variables:")
    print(json.dumps(variables, indent=2))
    
    try:
        response = requests.post(monday_url, headers=headers_monday, json={'query': query, 'variables': variables})
        
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        print(json.dumps(dict(response.headers), indent=2))
        
        print("Raw response:")
        print(response.text)
        
        try:
            response_data = response.json()
            if 'data' in response_data and 'create_item' in response_data['data']:
                print(f"Successfully created item with ID: {response_data['data']['create_item']['id']}")
                return response_data
            elif 'error_message' in response_data:
                print(f"Error from Monday.com: {response_data['error_message']}")
                return None
            else:
                print("Unexpected response structure:")
                print(json.dumps(response_data, indent=2))
                return None
        except json.JSONDecodeError:
            print("Failed to decode JSON response. Raw response:")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Monday.com: {e}")
        return None

def main():
    # Fetch data from Rivhit for item_group_id 12
    for item_group_id in range(1, 15):
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