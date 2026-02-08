import csv
import time
from serpapi import GoogleSearch
from tqdm import tqdm

def get_youtube_playlist_link(artist_name, api_key):
    """Get the first YouTube video link for an artist"""
    if not artist_name or artist_name.strip() == '':
        return ''
    
    try:
        params = {
            "engine": "youtube",
            "search_query": artist_name,
            "api_key": api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Try to get first video result
        if 'video_results' in results and len(results['video_results']) > 0:
            first_video = results['video_results'][0]
            print(first_video.get('link', ''))
            return first_video.get('link', '')
        
        # If no video results, return empty
        print(f"  ⚠️  No video found for: {artist_name}")
        return ''
        
    except Exception as e:
        print(f"  ❌ Error getting YouTube link for {artist_name}: {e}")
        return ''

def add_youtube_links_to_csv(input_csv, output_csv, api_key):
    """Read CSV with coordinates, add YouTube playlist links, and save to new CSV"""
    users = []
    
    # Read existing CSV
    print("Reading people_input_with_coords.csv...")
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            users.append(row)
    
    # Add new fieldname for YouTube link if it doesn't exist
    if 'youtube_video' not in fieldnames:
        new_fieldnames = list(fieldnames) + ['youtube_video']
    else:
        new_fieldnames = list(fieldnames)
    
    # Process each user and get YouTube video link
    print(f"\nGetting YouTube video links for {len(users)} artists...")
    for user in tqdm(users, desc="Processing artists"):
        artist_name = f"{user['first_name']} {user['last_name']}".strip()
        
        # Get YouTube video link
        youtube_link = get_youtube_playlist_link(artist_name, api_key)
        
        # Add to user dict
        user['youtube_video'] = youtube_link
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Write updated CSV
    print(f"\nWriting updated CSV to {output_csv}...")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(users)
    
    # Print summary
    links_found = sum(1 for u in users if u.get('youtube_video', ''))
    print(f"\n✓ Complete! Added YouTube links for {links_found}/{len(users)} artists")
    print(f"  Output saved to: {output_csv}")

if __name__ == "__main__":
    API_KEY = "c6e3b141e2b90d584f1f3c9405064e06e037852ccfd045fa1dd5f6aefb95d90b"
    INPUT_CSV = "./Data/04_people_input_with_coords.csv"
    OUTPUT_CSV = "./Data/04_people_input_with_coords.csv"  # Overwrite the same file
    
    add_youtube_links_to_csv(INPUT_CSV, OUTPUT_CSV, API_KEY)