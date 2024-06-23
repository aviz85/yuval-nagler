def main():
    # Fetch data from Rivhit
    rivhit_data = fetch_rivhit_data(1)  # Replace 1 with the actual item_group_id you want to fetch
    
    if rivhit_data:
        # Use only the first item from Rivhit
        test_item = rivhit_data[0]
        print("Using the first item from Rivhit:")
        print(json.dumps(test_item, indent=2, ensure_ascii=False))
        
        print("\nDetailed analysis of the first item:")
        for key, value in test_item.items():
            print(f"{key}: {value}")
            if isinstance(value, str):
                print(f"  Length: {len(value)}")
            elif isinstance(value, (int, float)):
                print(f"  Type: {type(value).__name__}")
        
        # Check for any empty or None values
        empty_fields = [key for key, value in test_item.items() if value in (None, '', 0)]
        if empty_fields:
            print("\nFields with empty or zero values:")
            for field in empty_fields:
                print(f"  {field}")
        else:
            print("\nNo empty or zero values found.")
    else:
        # If Rivhit fetch fails, use dummy data
        print("Failed to fetch data from Rivhit. Using dummy data instead.")
        test_item = generate_dummy_data()[0]
    
    # Transform and insert the item into Monday.com
    monday_data = transform_to_monday_schema(test_item)
    result = insert_to_monday(monday_data)
    if result:
        print(f"Successfully inserted item: {monday_data.get('name', 'Unknown')}")
    else:
        print(f"Failed to insert item: {monday_data.get('name', 'Unknown')}")
        
main()