from serpapi import GoogleSearch
import json
import csv
from tqdm import tqdm
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Create directory for raw API results
os.makedirs('./Data/raw_api_results', exist_ok=True)

# Thread lock for CSV writing
csv_lock = threading.Lock()

def process_artist(idx, artist_name, writer, csvfile):
    """Process a single artist and return the result."""
    artist_name = artist_name.strip()
    
    params = {
        "engine": "google_ai_mode",
        "q": f"{artist_name}, age, music related skills + abilities + occupations, proficiency in each, and current residence location (city, state)",
        "api_key": "c6e3b141e2b90d584f1f3c9405064e06e037852ccfd045fa1dd5f6aefb95d90b"
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Save raw API results to file
        safe_artist_name = "".join(c if c.isalnum() else "_" for c in artist_name)
        output_file = f'./Data/raw_api_results/{idx:03d}_{safe_artist_name}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Check if text_blocks exists
        if 'text_blocks' not in results or not results['text_blocks']:
            return f"No text_blocks found for {artist_name}"
            
        text_blocks = results["text_blocks"]
        desired_data = None
        for block in text_blocks:
            if block.get('type') == 'code_block':
                desired_data = block['code']
                break
        
        # Parse JSON if desired_data contains JSON formatted data
        if desired_data:
            try:
                parsed_data = json.loads(desired_data)
                
                # Extract and transform data to match schema
                formatted_data = {
                    'user_id': f'user_{idx:03d}',
                    'first_name': '',
                    'last_name': '',
                    'age': parsed_data.get('age', ''),
                    'genres': [],
                    'roles': [],
                    'skill_proficiency': [],
                    'skill_engagement': [],
                    'location': '',
                    'ok_not_local': '',
                    'weekly_time': '',
                    'considers_age': '',
                    'age_limit': ''
                }
                
                # Parse name into first and last
                if 'name' in parsed_data:
                    name_parts = parsed_data['name'].split()
                    if len(name_parts) >= 2:
                        formatted_data['first_name'] = name_parts[0]
                        formatted_data['last_name'] = ' '.join(name_parts[1:])
                    else:
                        formatted_data['first_name'] = parsed_data['name']
                
                # Extract location
                if 'location' in parsed_data:
                    if isinstance(parsed_data['location'], dict):
                        formatted_data['location'] = parsed_data['location'].get('hometown', '') or parsed_data['location'].get('current_activity', '')
                    else:
                        formatted_data['location'] = parsed_data['location']
                
                # Extract roles and proficiency from music_profile
                if 'music_profile' in parsed_data:
                    music_profile = parsed_data['music_profile']
                    
                    if 'occupations' in music_profile:
                        formatted_data['roles'] = music_profile['occupations']
                    
                    if 'skills_and_abilities' in music_profile:
                        for skill_item in music_profile['skills_and_abilities']:
                            if 'skill' in skill_item:
                                formatted_data['roles'].append(skill_item['skill'])
                                formatted_data['skill_proficiency'].append(skill_item.get('proficiency', 'Unknown'))
                
                # Convert lists to pipe-separated strings for CSV
                formatted_data['genres'] = '|'.join(formatted_data['genres']) if formatted_data['genres'] else ''
                formatted_data['roles'] = '|'.join(formatted_data['roles']) if formatted_data['roles'] else ''
                formatted_data['skill_proficiency'] = '|'.join(formatted_data['skill_proficiency']) if formatted_data['skill_proficiency'] else ''
                formatted_data['skill_engagement'] = '|'.join(formatted_data['skill_engagement']) if formatted_data['skill_engagement'] else ''
                
                # Write to CSV with thread lock
                with csv_lock:
                    writer.writerow(formatted_data)
                    csvfile.flush()
                
                return f"Successfully processed {artist_name}"
                
            except json.JSONDecodeError:
                return f"Failed to parse JSON for {artist_name}"
        else:
            return f"No code_block found for {artist_name}"
            
    except Exception as e:
        return f"Error processing {artist_name}: {str(e)}"

with open('./Data/generated_people.csv', 'r') as f:
    lines = f.readlines()

# Open output CSV file
with open('./Data/people_input.csv', 'w', newline='') as csvfile:
    fieldnames = ['user_id', 'first_name', 'last_name', 'age', 'genres', 'roles', 
                  'skill_proficiency', 'skill_engagement', 'location', 'ok_not_local', 
                  'weekly_time', 'considers_age', 'age_limit']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Process artists in parallel
    max_workers = 10  # Number of parallel threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = []
        for idx, line in enumerate(lines[1:], start=1):
            future = executor.submit(process_artist, idx, line, writer, csvfile)
            futures.append(future)
        
        # Process completed tasks with progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing artists"):
            result = future.result()
            if "Failed" in result or "Error" in result or "No" in result:
                print(f"\n{result}")
