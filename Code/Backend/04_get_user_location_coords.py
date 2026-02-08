import csv
import time
from serpapi import GoogleSearch
from tqdm import tqdm

def get_coordinates_for_location(location, api_key):
    """Get latitude and longitude coordinates for a given location using Google Maps API"""
    if not location or location == 'none':
        return None, None
    
    # Take the last location if pipe-separated (most recent/relevant)
    if '|' in location:
        location = location.split('|')[-1].strip()
    
    try:
        params = {
            "engine": "google_maps",
            "q": location,
            "type": "search",
            "api_key": api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Try to get coordinates from search results
        if 'place_results' in results and 'gps_coordinates' in results['place_results']:
            coords = results['place_results']['gps_coordinates']
            return coords.get('latitude'), coords.get('longitude')
        
        # Alternative: try local_results
        if 'local_results' in results and len(results['local_results']) > 0:
            first_result = results['local_results'][0]
            if 'gps_coordinates' in first_result:
                coords = first_result['gps_coordinates']
                return coords.get('latitude'), coords.get('longitude')
        
        # If no results, return None
        print(f"No coordinates found for: {location}")
        return None, None
        
    except Exception as e:
        print(f"Error getting coordinates for {location}: {e}")
        return None, None

def add_coordinates_to_csv(input_csv, output_csv, api_key):
    """Read CSV, add lat/lon coordinates for each user, and save to new CSV"""
    users = []
    
    # Read existing CSV
    print(f"Reading {input_csv}...")
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            users.append(row)
    
    # Add new fieldnames for coordinates
    new_fieldnames = list(fieldnames) + ['latitude', 'longitude']
    
    # Process each user and get coordinates
    print(f"\nGetting coordinates for {len(users)} users...")
    for user in tqdm(users, desc="Processing users"):
        location = user.get('location', '')
        user_name = f"{user['first_name']} {user['last_name']}".strip()
        
        # Get coordinates
        lat, lon = get_coordinates_for_location(location, api_key)
        
        # Add to user dict
        user['latitude'] = str(lat) if lat is not None else ''
        user['longitude'] = str(lon) if lon is not None else ''
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Write updated CSV
    print(f"\nWriting updated CSV to {output_csv}...")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(users)
    
    # Print summary
    coords_found = sum(1 for u in users if u['latitude'] and u['longitude'])
    print(f"\n✓ Complete! Added coordinates for {coords_found}/{len(users)} users")
    print(f"  Output saved to: {output_csv}")

if __name__ == "__main__":
    API_KEY = "c6e3b141e2b90d584f1f3c9405064e06e037852ccfd045fa1dd5f6aefb95d90b"
    INPUT_CSV = "./Data/people_input.csv"
    OUTPUT_CSV = "./Data/people_input_with_coords.csv"
    
    add_coordinates_to_csv(INPUT_CSV, OUTPUT_CSV, API_KEY)