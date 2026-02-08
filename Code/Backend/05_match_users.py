import csv
import json
import math
from collections import defaultdict

def parse_pipe_separated(value):
    """Parse pipe-separated values into a list"""
    if not value or value == '':
        return []
    return [item.strip() for item in value.split('|')]

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers using Haversine formula"""
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (ValueError, TypeError):
        return None
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def calculate_match_score(user1, user2):
    """Calculate match score between two users based on genres, roles, age, and location"""
    score = 0
    details = {
        'genre_matches': [],
        'role_matches': [],
        'age_compatible': True,
        'genre_score': 0,
        'role_score': 0,
        'age_score': 0,
        'location_score': 0,
        'distance_km': None
    }
    
    # Genre matching (weight: 30%)
    user1_genres = set(parse_pipe_separated(user1['genres']))
    user2_genres = set(parse_pipe_separated(user2['genres']))
    
    if user1_genres and user2_genres:
        genre_overlap = user1_genres.intersection(user2_genres)
        details['genre_matches'] = list(genre_overlap)
        # Calculate genre score based on percentage of overlap
        genre_score = len(genre_overlap) / max(len(user1_genres), len(user2_genres)) * 30
        details['genre_score'] = round(genre_score, 2)
        score += genre_score
    
    # Role matching (weight: 30%)
    user1_roles = set(parse_pipe_separated(user1['roles']))
    user2_roles = set(parse_pipe_separated(user2['roles']))
    
    if user1_roles and user2_roles:
        role_overlap = user1_roles.intersection(user2_roles)
        details['role_matches'] = list(role_overlap)
        # Calculate role score based on percentage of overlap
        role_score = len(role_overlap) / max(len(user1_roles), len(user2_roles)) * 30
        details['role_score'] = round(role_score, 2)
        score += role_score
    
    # Age compatibility (weight: 15%)
    age_score = 15  # Default full score if age doesn't matter
    
    # Check if user1 considers age
    if user1.get('considers_age', '').upper() == 'TRUE':
        user1_age = user1.get('age', '')
        user2_age = user2.get('age', '')
        
        if user1_age and user2_age:
            try:
                age1 = int(user1_age)
                age2 = int(user2_age)
                age_diff = abs(age1 - age2)
                
                age_limit = user1.get('age_limit', '999')
                try:
                    limit = int(age_limit)
                    if limit == 999:  # No age limit
                        age_score = 15
                        details['age_compatible'] = True
                    elif age_diff <= limit:
                        # Full score if within limit
                        age_score = 15
                        details['age_compatible'] = True
                    else:
                        # Partial score based on how close to limit
                        age_score = max(0, 15 - (age_diff - limit) * 1.5)
                        details['age_compatible'] = False
                except ValueError:
                    pass
            except ValueError:
                # If ages can't be parsed, give neutral score
                age_score = 7.5
    
    details['age_score'] = round(age_score, 2)
    score += age_score
    
    # Location proximity (weight: 25%)
    location_score = 25  # Default full score
    
    # Get coordinates
    lat1 = user1.get('latitude', '')
    lon1 = user1.get('longitude', '')
    lat2 = user2.get('latitude', '')
    lon2 = user2.get('longitude', '')
    
    if lat1 and lon1 and lat2 and lon2:
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        if distance is not None:
            details['distance_km'] = round(distance, 2)
            
            # Check if user is ok with non-local collaborators
            ok_not_local = user1.get('ok_not_local', '').upper() == 'TRUE'
            
            if ok_not_local:
                # If ok with non-local, distance has less impact
                # Close proximity still gets bonus, but far distance isn't heavily penalized
                if distance < 50:  # Within 50km - full score
                    location_score = 25
                elif distance < 200:  # Within 200km - high score
                    location_score = 22
                elif distance < 500:  # Within 500km - good score
                    location_score = 20
                else:  # Beyond 500km - moderate score (not heavily penalized)
                    location_score = 15
            else:
                # If prefers local, distance matters more
                if distance < 25:  # Within 25km - full score
                    location_score = 25
                elif distance < 50:  # Within 50km - high score
                    location_score = 20
                elif distance < 100:  # Within 100km - moderate score
                    location_score = 15
                elif distance < 200:  # Within 200km - low score
                    location_score = 10
                else:  # Beyond 200km - very low score
                    location_score = 5
    
    details['location_score'] = round(location_score, 2)
    score += location_score
    
    return score, details

def find_matches_for_all_users(csv_path):
    """Find top 10 matches for each user"""
    # Read all users
    users = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    
    # Calculate matches for each user
    all_matches = {}
    
    for i, user in enumerate(users):
        user_id = user['user_id']
        matches = []
        
        # Compare with all other users
        for j, other_user in enumerate(users):
            if i == j:  # Skip self
                continue
            
            score, details = calculate_match_score(user, other_user)
            
            match_info = {
                'user_id': other_user['user_id'],
                'name': f"{other_user['first_name']} {other_user['last_name']}".strip(),
                'score': round(score, 2),
                'genre_matches': details['genre_matches'],
                'role_matches': details['role_matches'],
                'age_compatible': details['age_compatible'],
                'genre_score': details['genre_score'],
                'role_score': details['role_score'],
                'age_score': details['age_score'],
                'location_score': details['location_score'],
                'distance_km': details['distance_km'],
                'location': other_user['location']
            }
            
            matches.append(match_info)
        
        # Sort by score (descending) and take top 10
        matches.sort(key=lambda x: x['score'], reverse=True)
        top_10 = matches[:10]
        
        all_matches[user_id] = {
            'user_id': user_id,
            'name': f"{user['first_name']} {user['last_name']}".strip(),
            'genres': parse_pipe_separated(user['genres']),
            'roles': parse_pipe_separated(user['roles']),
            'age': user.get('age', 'N/A'),
            'considers_age': user.get('considers_age', ''),
            'age_limit': user.get('age_limit', ''),
            'location': user['location'],
            'top_matches': top_10
        }
    
    return all_matches

def save_matches_to_json(matches, output_path):
    """Save matches to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(matches, f, indent=2)
    print(f"Matches saved to {output_path}")

def save_matches_to_csv(matches, output_path):
    """Save matches to CSV file (flattened format)"""
    with open(output_path, 'w', newline='') as f:
        fieldnames = [
            'user_id', 'user_name', 'match_rank', 'matched_user_id', 'matched_user_name',
            'match_score', 'genre_score', 'role_score', 'age_score', 'location_score',
            'distance_km', 'genre_matches', 'role_matches', 'age_compatible', 'matched_location'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for user_id, user_data in matches.items():
            for rank, match in enumerate(user_data['top_matches'], start=1):
                row = {
                    'user_id': user_id,
                    'user_name': user_data['name'],
                    'match_rank': rank,
                    'matched_user_id': match['user_id'],
                    'matched_user_name': match['name'],
                    'match_score': match['score'],
                    'genre_score': match['genre_score'],
                    'role_score': match['role_score'],
                    'age_score': match['age_score'],
                    'location_score': match['location_score'],
                    'distance_km': match['distance_km'] if match['distance_km'] is not None else '',
                    'genre_matches': '|'.join(match['genre_matches']),
                    'role_matches': '|'.join(match['role_matches']),
                    'age_compatible': match['age_compatible'],
                    'matched_location': match['location']
                }
                writer.writerow(row)
    
    print(f"Matches saved to {output_path}")

def print_sample_matches(matches, num_users=3):
    """Print sample matches for first few users"""
    print("\n=== SAMPLE MATCHES ===\n")
    
    for i, (user_id, user_data) in enumerate(matches.items()):
        if i >= num_users:
            break
        
        print(f"\n{user_data['name']} ({user_id})")
        print(f"  Genres: {', '.join(user_data['genres'][:3])}...")
        print(f"  Roles: {', '.join(user_data['roles'][:3])}...")
        print(f"  Age: {user_data['age']} | Considers Age: {user_data['considers_age']} | Age Limit: {user_data['age_limit']}")
        print(f"\n  Top 10 Matches:")
        print(f"  {'Rank':<6} {'Name':<25} {'Score':<8} {'Genre':<7} {'Role':<7} {'Age':<7} {'Loc':<7} {'Dist (km)':<12}")
        print(f"  {'-'*6} {'-'*25} {'-'*8} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*12}")
        
        for rank, match in enumerate(user_data['top_matches'], start=1):
            dist_str = f"{match['distance_km']:.0f}" if match['distance_km'] is not None else 'N/A'
            print(f"  {rank:<6} {match['name'][:25]:<25} {match['score']:<8.2f} {match['genre_score']:<7.2f} {match['role_score']:<7.2f} {match['age_score']:<7.2f} {match['location_score']:<7.2f} {dist_str:<12}")
            if match['genre_matches']:
                print(f"         → Shared genres: {', '.join(match['genre_matches'][:3])}")
            if match['role_matches']:
                print(f"         → Shared roles: {', '.join(match['role_matches'][:3])}")
            if match['distance_km'] is not None:
                print(f"         → Distance: {match['distance_km']:.1f} km ({match['location']})")

if __name__ == "__main__":
    csv_path = './Data/people_input_with_coords.csv'
    json_output = './Data/user_matches.json'
    csv_output = './Data/user_matches.csv'
    
    print("Finding matches for all users...")
    matches = find_matches_for_all_users(csv_path)
    
    print(f"\nProcessed {len(matches)} users")
    
    # Save to JSON (detailed format)
    save_matches_to_json(matches, json_output)
    
    # Save to CSV (flattened format)
    save_matches_to_csv(matches, csv_output)
    
    # Print sample matches
    print_sample_matches(matches, num_users=5)
    
    print("\n✓ Matching complete!")
