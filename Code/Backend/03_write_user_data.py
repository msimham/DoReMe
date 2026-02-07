import json
import csv
import os
import re
import random
from tqdm import tqdm
from thefuzz import fuzz, process
import spacy

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Standard role categories for fuzzy matching
STANDARD_ROLES = [
    'singer', 'songwriter', 'composer', 'producer', 'pianist', 
    'guitarist', 'bassist', 'drummer', 'dancer', 'actor',
    'multi-instrumentalist', 'lyricist', 'vocalist', 'arranger',
    'conductor', 'dj', 'beatboxer', 'rapper', 'keyboardist'
]

# Standard genres for fuzzy matching
STANDARD_GENRES = [
    'pop', 'rock', 'country', 'rap', 'hip hop', 'r&b', 'rnb',
    'soul', 'jazz', 'blues', 'electronic', 'dance', 'indie', 
    'alternative', 'classical', 'folk', 'reggae', 'metal', 
    'punk', 'disco', 'funk', 'gospel', 'latin', 'techno', 'house'
]

def extract_entities_with_spacy(text):
    """Extract named entities using spaCy NER"""
    doc = nlp(text)
    entities = {
        'locations': [],
        'persons': [],
        'dates': [],
        'ages': []
    }
    
    for ent in doc.ents:
        if ent.label_ == 'GPE' or ent.label_ == 'LOC':  # Geopolitical entity or location
            entities['locations'].append(ent.text)
        elif ent.label_ == 'PERSON':
            entities['persons'].append(ent.text)
        elif ent.label_ == 'DATE':
            # Try to extract age from date mentions
            age_match = re.search(r'(\d+)\s+years?\s+old', ent.text)
            if age_match:
                entities['ages'].append(age_match.group(1))
    
    return entities

def normalize_proficiency(prof_text):
    """Normalize proficiency to: beginner, intermediate, advanced, expert"""
    if not prof_text:
        return ''
    prof_lower = prof_text.lower()
    
    if any(word in prof_lower for word in ['expert', 'master', 'virtuoso', 'elite', 'legend']):
        return 'expert'
    elif any(word in prof_lower for word in ['advanced', 'proficient', 'highly proficient', 'competent']):
        return 'advanced'
    elif any(word in prof_lower for word in ['intermediate', 'moderate']):
        return 'intermediate'
    elif any(word in prof_lower for word in ['beginner', 'novice', 'basic']):
        return 'beginner'
    else:
        return 'advanced'  # Default if unclear

def infer_engagement(prof_text):
    """Infer engagement level from proficiency: hobbyist, serious hobbyist, semi-professional, professional"""
    if not prof_text:
        return ''
    prof_lower = prof_text.lower()
    
    if any(word in prof_lower for word in ['professional', 'expert', 'master', 'legend', 'virtuoso', 'elite']):
        return 'professional'
    elif any(word in prof_lower for word in ['semi-professional', 'advanced', 'proficient']):
        return 'semi-professional'
    elif any(word in prof_lower for word in ['serious', 'dedicated', 'competent']):
        return 'serious hobbyist'
    else:
        return 'hobbyist'

def is_valid_role(role_text):
    """Check if text looks like a valid musical role"""
    if not role_text or len(role_text) < 3:
        return False
    
    role_lower = role_text.lower()
    
    # Filter out obvious non-roles
    invalid_patterns = [
        'proficiency', 'description', 'notes', 'level', 'context',
        'achievements', 'notable', 'details', 'key abilities',
        'and ', 'or ', 'the ', '&', 'estimated', 'ability'
    ]
    
    for pattern in invalid_patterns:
        if pattern in role_lower:
            return False
    
    # Check if it ends with punctuation (likely incomplete sentence)
    if role_text.endswith(('.', ',', ';', '!')):
        return False
    
    return True

def clean_role_text(role_text):
    """Clean and extract actual role from messy text"""
    if not role_text:
        return ''
    
    # Remove common suffixes
    role_text = re.sub(r',?\s+and\s+.*$', '', role_text)  # Remove "and ..." suffixes
    role_text = re.sub(r',?\s+or\s+.*$', '', role_text)   # Remove "or ..." suffixes
    role_text = role_text.strip(' ,.;')
    
    return role_text

def normalize_role(role_text):
    """Normalize role to standard categories using fuzzy matching"""
    if not role_text:
        return ''
    
    # Clean first
    role_text = clean_role_text(role_text)
    
    # Check if valid
    if not is_valid_role(role_text):
        return ''
    
    role_lower = role_text.lower().strip()
    
    # First try exact keyword matching (faster)
    role_mapping = {
        'singer': ['singer', 'vocalist', 'vocal'],
        'songwriter': ['songwriter', 'songwriting', 'lyricist'],
        'composer': ['composer', 'composing', 'composition'],
        'producer': ['producer', 'production', 'record producer'],
        'pianist': ['pianist', 'piano', 'keyboard'],
        'guitarist': ['guitarist', 'guitar'],
        'bassist': ['bassist', 'bass'],
        'drummer': ['drummer', 'drums', 'percussion'],
        'dancer': ['dancer', 'dancing', 'choreographer'],
        'actor': ['actor', 'actress', 'acting'],
        'multi-instrumentalist': ['multi-instrumentalist', 'multi instrumentalist'],
        'musician': ['musician'],
        'rapper': ['rapper', 'rapping'],
        'arranger': ['arranger', 'arrangement'],
    }
    
    for standard_role, keywords in role_mapping.items():
        if any(keyword in role_lower for keyword in keywords):
            return standard_role
    
    # If no exact match, use fuzzy matching
    match = process.extractOne(role_lower, STANDARD_ROLES, scorer=fuzz.token_set_ratio)
    if match and match[1] >= 75:  # Increased threshold to 75%
        return match[0]
    
    return ''  # Return empty if no good match

def extract_genres(text_blocks):
    """Extract music genres using fuzzy matching"""
    genres = []
    
    for block in text_blocks:
        snippet = block.get('snippet', '').lower()
        
        # Find potential genre mentions using fuzzy matching
        words = snippet.split()
        for i, word in enumerate(words):
            # Check 1-3 word phrases
            for length in [1, 2, 3]:
                if i + length <= len(words):
                    phrase = ' '.join(words[i:i+length])
                    match = process.extractOne(phrase, STANDARD_GENRES, scorer=fuzz.ratio)
                    if match and match[1] >= 85:  # 85% similarity threshold for genres
                        if match[0] not in genres:
                            genres.append(match[0])
    
    return genres[:5]  # Limit to top 5 genres

def clean_location(location_text):
    """Clean and validate location to ensure city, state, country format"""
    if not location_text:
        return 'none'
    
    location = location_text.strip()
    
    # Remove content in parentheses (often contains extra details)
    location = re.sub(r'\([^)]*\)', '', location)
    
    # Skip if contains street address indicators
    street_indicators = [
        'drive', 'street', 'avenue', 'road', 'boulevard', 'lane', 'way', 'court',
        'place', 'circle', 'parkway', 'terrace', 'dr.', 'st.', 'ave.', 'rd.', 'blvd.'
    ]
    if any(indicator in location.lower() for indicator in street_indicators):
        return 'none'
    
    # Parse location parts
    parts = [p.strip() for p in location.split(',')]
    
    # Filter out empty parts
    parts = [p for p in parts if p]
    
    if len(parts) >= 3:
        # Has city, state, country - keep first three
        location = f"{parts[0]}, {parts[1]}, {parts[2]}"
    elif len(parts) == 2:
        # Has city, state/country - keep as is
        location = f"{parts[0]}, {parts[1]}"
    elif len(parts) == 1:
        # Only one part - could be city or country
        location = parts[0]
    else:
        return 'none'
    
    # Skip very short locations (likely noise)
    if len(location) < 4:
        return 'none'
    
    # Skip if it's all numbers (like zip codes)
    if location.replace(',', '').replace(' ', '').isdigit():
        return 'none'
    
    return location

def extract_location_with_spacy(text_blocks):
    """Extract location using spaCy NER with city/state/country filtering"""
    all_text = ' '.join([block.get('snippet', '') for block in text_blocks])
    entities = extract_entities_with_spacy(all_text)
    
    # Filter for major cities/states/countries
    for location in entities['locations']:
        cleaned = clean_location(location)
        if cleaned and cleaned != 'none':
            return cleaned
    
    return 'none'

def is_deceased(text_blocks):
    """Check if the person is deceased based on text"""
    all_text = ' '.join([block.get('snippet', '') for block in text_blocks]).lower()
    deceased_indicators = [
        'died', 'death', 'deceased', 'passed away', 'late ', 'legacy of',
        r'\d{4}[-–]\d{4}',  # Birth-death year pattern
    ]
    
    for indicator in deceased_indicators:
        if re.search(indicator, all_text):
            return True
    return False

def generate_default_proficiency(num_roles):
    """Generate varied proficiency levels for roles"""
    proficiencies = ['beginner', 'intermediate', 'advanced', 'expert']
    # Weight towards higher proficiency for musicians
    weights = [0.1, 0.2, 0.4, 0.3]
    return [random.choices(proficiencies, weights=weights)[0] for _ in range(num_roles)]

def generate_default_engagement(num_roles):
    """Generate varied engagement levels for roles"""
    engagements = ['hobbyist', 'serious hobbyist', 'semi-professional', 'professional']
    # Weight towards professional for established musicians
    weights = [0.1, 0.2, 0.3, 0.4]
    return [random.choices(engagements, weights=weights)[0] for _ in range(num_roles)]

def generate_default_values():
    """Generate random default values for missing fields"""
    return {
        'ok_not_local': random.choice(['true', 'false']),
        'weekly_time': str(random.choice([5, 10, 15, 20, 25, 30, 35, 40])),
        'considers_age': random.choice(['true', 'false']),
        'age_limit': str(random.choice([5, 10, 15, 20, 999]))  # 999 means no limit
    }

def extract_age_with_spacy(text_blocks):
    """Extract age using spaCy NER and regex"""
    all_text = ' '.join([block.get('snippet', '') for block in text_blocks])
    entities = extract_entities_with_spacy(all_text)
    
    # Check extracted ages first
    if entities['ages']:
        age = int(entities['ages'][0])
        if 10 <= age <= 100:
            return entities['ages'][0]
    
    # Fallback to regex patterns - prioritize "X years old" format
    age_patterns = [
        (r'(\d+)\s+years\s+old', 1),  # Priority 1
        (r'age[:\s]+(\d+)', 1),       # Priority 2
        (r'Age:\s*(\d+)', 1),         # Priority 3
        (r'\(age\s+(\d+)\)', 1),      # Priority 4
        (r'turned\s+(\d+)', 1),       # Priority 5
        (r'born.*?(\d{4})', 2),       # Birth year - lowest priority
    ]
    
    for pattern, priority in age_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            age_value = match.group(1)
            age_int = int(age_value)
            
            # If it's a birth year (4 digits), calculate age
            if priority == 2 and age_int > 1900 and age_int <= 2024:
                age_int = 2026 - age_int
            
            # Validate reasonable age range
            if 10 <= age_int <= 100:
                return str(age_int)
    
    return ''

# Directory with raw API results
raw_results_dir = './Data/raw_api_results'

# Get all JSON files sorted by filename
json_files = sorted([f for f in os.listdir(raw_results_dir) if f.endswith('.json')])

# Open output CSV file
with open('./Data/people_input.csv', 'w', newline='') as csvfile:
    fieldnames = ['user_id', 'first_name', 'last_name', 'age', 'genres', 'roles', 
                  'skill_proficiency', 'skill_engagement', 'location', 'ok_not_local', 
                  'weekly_time', 'considers_age', 'age_limit']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Process each JSON file
    for json_file in tqdm(json_files, desc="Processing API results"):
        file_path = os.path.join(raw_results_dir, json_file)
        
        # Extract index from filename (e.g., "001_Artist_Name.json" -> 1)
        idx = int(json_file.split('_')[0])
        artist_name = '_'.join(json_file.split('_')[1:]).replace('.json', '').replace('_', ' ')
        
        # Load the JSON file
        with open(file_path, 'r') as f:
            results = json.load(f)
        
        # Check if text_blocks exists
        if 'text_blocks' not in results or not results['text_blocks']:
            print(f"No text_blocks found in {json_file}, skipping...")
            continue
            
        text_blocks = results["text_blocks"]
        
        # Extract using spaCy
        spacy_location = extract_location_with_spacy(text_blocks)
        spacy_age = extract_age_with_spacy(text_blocks)
        
        # Check if deceased and override location
        deceased = is_deceased(text_blocks)
        if deceased:
            spacy_location = 'none'
        
        # Extract genres from all text blocks
        extracted_genres = extract_genres(text_blocks)
        
        # Try to find code_block first (JSON format)
        desired_data = None
        for block in text_blocks:
            if block.get('type') == 'code_block':
                desired_data = block['code']
                break
        
        # If code_block found, parse as JSON
        if desired_data:
            try:
                parsed_data = json.loads(desired_data)
                
                # Extract and transform data to match schema
                formatted_data = {
                    'user_id': f'user_{idx:03d}',
                    'first_name': '',
                    'last_name': '',
                    'age': parsed_data.get('age', '') or spacy_age,
                    'genres': extracted_genres,
                    'roles': [],
                    'skill_proficiency': [],
                    'skill_engagement': [],
                    'location': 'none',
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
                
                # Extract location (prefer parsed data, fallback to spaCy)
                if 'location' in parsed_data:
                    if isinstance(parsed_data['location'], dict):
                        loc = parsed_data['location'].get('hometown', '') or parsed_data['location'].get('current_activity', '')
                        formatted_data['location'] = clean_location(loc)
                    else:
                        formatted_data['location'] = clean_location(parsed_data['location'])
                if not formatted_data['location'] or formatted_data['location'] == 'none':
                    formatted_data['location'] = spacy_location
                
                # Extract roles and proficiency from music_profile
                if 'music_profile' in parsed_data:
                    music_profile = parsed_data['music_profile']
                    
                    if 'occupations' in music_profile:
                        for occ in music_profile['occupations']:
                            normalized_role = normalize_role(occ)
                            if normalized_role not in formatted_data['roles']:
                                formatted_data['roles'].append(normalized_role)
                    
                    if 'skills_and_abilities' in music_profile:
                        for skill_item in music_profile['skills_and_abilities']:
                            if 'skill' in skill_item:
                                role = normalize_role(skill_item['skill'])
                                prof = skill_item.get('proficiency', '')
                                
                                if role not in formatted_data['roles']:
                                    formatted_data['roles'].append(role)
                                    formatted_data['skill_proficiency'].append(normalize_proficiency(prof))
                                    formatted_data['skill_engagement'].append(infer_engagement(prof))
                
                # Ensure at least one role (singer as default)
                if not formatted_data['roles']:
                    formatted_data['roles'].append('singer')
                
                # Ensure all lists are same length with varied defaults
                while len(formatted_data['skill_proficiency']) < len(formatted_data['roles']):
                    default_profs = generate_default_proficiency(len(formatted_data['roles']) - len(formatted_data['skill_proficiency']))
                    formatted_data['skill_proficiency'].extend(default_profs)
                while len(formatted_data['skill_engagement']) < len(formatted_data['roles']):
                    default_engs = generate_default_engagement(len(formatted_data['roles']) - len(formatted_data['skill_engagement']))
                    formatted_data['skill_engagement'].extend(default_engs)
                
                # Generate default values for missing fields
                defaults = generate_default_values()
                formatted_data['ok_not_local'] = defaults['ok_not_local']
                formatted_data['weekly_time'] = defaults['weekly_time']
                formatted_data['considers_age'] = defaults['considers_age']
                formatted_data['age_limit'] = defaults['age_limit']
                
                # Override location if deceased
                if deceased:
                    formatted_data['location'] = 'none'
                
                # Convert lists to pipe-separated strings for CSV
                formatted_data['genres'] = '|'.join(formatted_data['genres']) if formatted_data['genres'] else ''
                formatted_data['roles'] = '|'.join(formatted_data['roles']) if formatted_data['roles'] else ''
                formatted_data['skill_proficiency'] = '|'.join(formatted_data['skill_proficiency']) if formatted_data['skill_proficiency'] else ''
                formatted_data['skill_engagement'] = '|'.join(formatted_data['skill_engagement']) if formatted_data['skill_engagement'] else ''
                
                # Write to CSV
                writer.writerow(formatted_data)
                csvfile.flush()
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON for {json_file}: {e}")
                continue
        else:
            # No code_block, try to parse from list or table structure
            formatted_data = {
                'user_id': f'user_{idx:03d}',
                'first_name': '',
                'last_name': '',
                'age': spacy_age,
                'genres': extracted_genres,
                'roles': [],
                'skill_proficiency': [],
                'skill_engagement': [],
                'location': spacy_location,
                'ok_not_local': '',
                'weekly_time': '',
                'considers_age': '',
                'age_limit': ''
            }
            
            # Parse from text_blocks structure
            for block in text_blocks:
                # Handle table structures (like Madonna's data)
                if block.get('type') == 'table' and 'table' in block:
                    for row in block['table']:
                        if len(row) >= 2:
                            key = row[0].lower()
                            value = row[1]
                            
                            # Skip header rows
                            if 'proficiency' in key or 'description' in key or 'notes' in key or 'level' in key or 'context' in key:
                                continue
                            
                            if 'occupation' in key or 'skill' in key or 'role' in key:
                                # This might be roles/skills
                                if isinstance(value, str):
                                    cleaned_role = normalize_role(value)
                                    if cleaned_role and cleaned_role not in formatted_data['roles']:
                                        formatted_data['roles'].append(cleaned_role)
                
                # Handle list structures
                elif block.get('type') == 'list' and 'list' in block:
                    for item in block['list']:
                        snippet = item.get('snippet', '')
                        
                        # Try to extract age from current level
                        if 'Age:' in snippet and not formatted_data['age']:
                            age_match = re.search(r'Age:\s*(\d+)', snippet)
                            if age_match:
                                formatted_data['age'] = age_match.group(1)
                        
                        # Try to extract location from current level
                        if formatted_data['location'] == 'none' and ('Location:' in snippet or 'Resides' in snippet or 'lives in' in snippet.lower()):
                            # Clean location text
                            loc_text = snippet.replace('Location:', '').replace('Resides primarily in', '').replace('Resides in', '').strip()
                            # Get location before period (but keep comma for city, state format)
                            loc_text = loc_text.split('.')[0].strip()
                            cleaned_loc = clean_location(loc_text)
                            if cleaned_loc and cleaned_loc != 'none':
                                formatted_data['location'] = cleaned_loc
                        
                        # Extract nested data if available
                        if 'list' in item:
                            for sub_item in item['list']:
                                sub_snippet = sub_item.get('snippet', '')
                                
                                # Extract age
                                if sub_snippet.startswith('Age:') and not formatted_data['age']:
                                    age_text = sub_snippet.replace('Age:', '').strip()
                                    age_match = re.search(r'\d+', age_text)
                                    if age_match:
                                        formatted_data['age'] = age_match.group()
                                
                                # Extract occupations
                                elif sub_snippet.startswith('Occupations:'):
                                    occ_text = sub_snippet.replace('Occupations:', '').strip()
                                    roles = [normalize_role(o.strip()) for o in occ_text.split(',') if o.strip()]
                                    for role in roles:
                                        if role and role not in formatted_data['roles']:
                                            formatted_data['roles'].append(role)
                                
                                # Extract location
                                elif sub_snippet.startswith('Location:') or 'Resides' in sub_snippet:
                                    loc_text = sub_snippet.replace('Location:', '').replace('Resides primarily in', '').replace('Resides in', '').strip()
                                    # Get location before period
                                    loc_text = loc_text.split('.')[0].strip()
                                    cleaned_loc = clean_location(loc_text)
                                    if cleaned_loc and cleaned_loc != 'none' and formatted_data['location'] == 'none':
                                        formatted_data['location'] = cleaned_loc
                                
                                # Extract music skills with proficiency
                                elif 'Music Skills' in sub_snippet and 'list' in sub_item:
                                    for skill_item in sub_item.get('list', []):
                                        skill_snippet = skill_item.get('snippet', '')
                                        if ':' in skill_snippet:
                                            skill_parts = skill_snippet.split(':', 1)
                                            skill_name = skill_parts[0].strip()
                                            skill_prof = skill_parts[1].strip().split(';')[0].strip() if len(skill_parts) > 1 else ''
                                            
                                            role = normalize_role(skill_name)
                                            if role and role not in formatted_data['roles']:
                                                formatted_data['roles'].append(role)
                                                formatted_data['skill_proficiency'].append(normalize_proficiency(skill_prof))
                                                formatted_data['skill_engagement'].append(infer_engagement(skill_prof))
                                
                                # Check for nested lists with more skills
                                elif 'list' in sub_item:
                                    for nested_item in sub_item.get('list', []):
                                        nested_snippet = nested_item.get('snippet', '')
                                        if ':' in nested_snippet:
                                            skill_parts = nested_snippet.split(':', 1)
                                            skill_name = skill_parts[0].strip()
                                            skill_prof = skill_parts[1].strip().split(';')[0].strip() if len(skill_parts) > 1 else ''
                                            # Only add if looks like a skill
                                            if any(word in skill_name.lower() for word in ['vocal', 'guitar', 'bass', 'drum', 'piano', 'song', 'write', 'produc', 'dance', 'instrument']):
                                                role = normalize_role(skill_name)
                                                if role not in formatted_data['roles']:
                                                    formatted_data['roles'].append(role)
                                                    formatted_data['skill_proficiency'].append(normalize_proficiency(skill_prof))
                                                    formatted_data['skill_engagement'].append(infer_engagement(skill_prof))
                
                # Handle paragraph structures that might contain age/location
                elif block.get('type') == 'paragraph':
                    snippet = block.get('snippet', '')
                    
                    # Try to extract age
                    if not formatted_data['age']:
                        age_patterns = [
                            r'(\d+)\s+years old',
                            r'age\s+(\d+)',
                            r'Age:\s*(\d+)',
                            r'\(age\s+(\d+)\)'
                        ]
                        for pattern in age_patterns:
                            age_match = re.search(pattern, snippet, re.IGNORECASE)
                            if age_match:
                                formatted_data['age'] = age_match.group(1)
                                break
                    
                    # Try to extract location
                    if formatted_data['location'] == 'none':
                        # Look for common location patterns
                        location_patterns = [
                            r'in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z][a-z]+)',
                            r'from ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z][a-z]+)',
                            r'lives in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                            r'resides in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
                        ]
                        for pattern in location_patterns:
                            loc_match = re.search(pattern, snippet)
                            if loc_match:
                                cleaned_loc = clean_location(loc_match.group(1))
                                if cleaned_loc and cleaned_loc != 'none':
                                    formatted_data['location'] = cleaned_loc
                                    break
            
            # Parse name from artist_name if we have data
            if formatted_data['age'] or formatted_data['roles'] or formatted_data['location']:
                name_parts = artist_name.split()
                if len(name_parts) >= 2:
                    formatted_data['first_name'] = name_parts[0]
                    formatted_data['last_name'] = ' '.join(name_parts[1:])
                else:
                    formatted_data['first_name'] = artist_name
                
                # Ensure at least one role (singer as default)
                if not formatted_data['roles']:
                    formatted_data['roles'].append('singer')
                
                # Ensure skill_proficiency and skill_engagement match roles length with varied defaults
                while len(formatted_data['skill_proficiency']) < len(formatted_data['roles']):
                    default_profs = generate_default_proficiency(len(formatted_data['roles']) - len(formatted_data['skill_proficiency']))
                    formatted_data['skill_proficiency'].extend(default_profs)
                while len(formatted_data['skill_engagement']) < len(formatted_data['roles']):
                    default_engs = generate_default_engagement(len(formatted_data['roles']) - len(formatted_data['skill_engagement']))
                    formatted_data['skill_engagement'].extend(default_engs)
                
                # Generate default values for missing fields
                defaults = generate_default_values()
                formatted_data['ok_not_local'] = defaults['ok_not_local']
                formatted_data['weekly_time'] = defaults['weekly_time']
                formatted_data['considers_age'] = defaults['considers_age']
                formatted_data['age_limit'] = defaults['age_limit']
                
                # Override location if deceased
                if deceased:
                    formatted_data['location'] = 'none'
                
                # Convert lists to pipe-separated strings for CSV
                formatted_data['genres'] = '|'.join(formatted_data['genres']) if formatted_data['genres'] else ''
                formatted_data['roles'] = '|'.join(formatted_data['roles']) if formatted_data['roles'] else ''
                formatted_data['skill_proficiency'] = '|'.join(formatted_data['skill_proficiency']) if formatted_data['skill_proficiency'] else ''
                formatted_data['skill_engagement'] = '|'.join(formatted_data['skill_engagement']) if formatted_data['skill_engagement'] else ''
                
                # Write to CSV
                writer.writerow(formatted_data)
                csvfile.flush()
            else:
                print(f"Could not extract usable data from {json_file}")

print(f"\nProcessed {len(json_files)} files. CSV written to ./Data/people_input.csv")
