import pandas as pd
import numpy as np

# --- Paths ---
METADATA_MATCHES_CSV = "./Results/05_user_matches.csv"
AUDIO_MATCHES_CSV = "./Results/06_audio_user_matches.csv"
OUTPUT_CSV = "./Results/07_final_user_matches.csv"

# --- Weights (must sum to 100) ---
LOCATION_WEIGHT = 30
GENRE_WEIGHT = 25
AUDIO_WEIGHT = 20
ROLE_WEIGHT = 15
AGE_WEIGHT = 10

print("Loading match files...")
metadata_df = pd.read_csv(METADATA_MATCHES_CSV)
audio_df = pd.read_csv(AUDIO_MATCHES_CSV)

print(f"✅ Loaded {len(metadata_df)} metadata matches")
print(f"✅ Loaded {len(audio_df)} audio matches\n")

# --- Build lookup dictionaries ---
print("Building match score lookups...")

# Metadata matches: {(user_id, matched_user_id): row_data}
metadata_lookup = {}
for _, row in metadata_df.iterrows():
    key = (row['user_id'], row['matched_user_id'])
    metadata_lookup[key] = row

# Audio matches: {(user_id, matched_user_id): audio_score}
audio_lookup = {}
for _, row in audio_df.iterrows():
    user_id = row['user_id']
    # Extract all 10 matches for this user
    for rank in range(1, 11):
        match_id_col = f'match_{rank}_user_id'
        score_col = f'match_{rank}_score'
        
        if pd.notna(row.get(match_id_col)):
            matched_id = row[match_id_col]
            audio_score = row[score_col]
            key = (user_id, matched_id)
            audio_lookup[key] = audio_score

print(f"✅ Built lookups: {len(metadata_lookup)} metadata pairs, {len(audio_lookup)} audio pairs\n")

# --- Consolidate matches ---
print("Consolidating matches with weighted scoring...")
consolidated_matches = []

# Get unique users
unique_users = metadata_df['user_id'].unique()

for user_id in unique_users:
    user_name = metadata_df[metadata_df['user_id'] == user_id]['user_name'].iloc[0]
    
    # Get all potential matches for this user from metadata
    user_metadata_matches = metadata_df[metadata_df['user_id'] == user_id]
    
    match_scores = []
    
    for _, meta_row in user_metadata_matches.iterrows():
        matched_id = meta_row['matched_user_id']
        matched_name = meta_row['matched_user_name']
        
        # Extract component scores (normalize to 0-1 range)
        location_score = meta_row['location_score'] / 25.0  # Max 25 points
        genre_score = meta_row['genre_score'] / 30.0  # Max 30 points
        role_score = meta_row['role_score'] / 30.0  # Max 30 points
        age_score = meta_row['age_score'] / 15.0  # Max 15 points
        
        # Get audio score (already 0-1 range from cosine similarity)
        audio_score = audio_lookup.get((user_id, matched_id), 0.0)
        
        # Calculate weighted final score (0-100 scale)
        final_score = (
            location_score * LOCATION_WEIGHT +
            genre_score * GENRE_WEIGHT +
            audio_score * AUDIO_WEIGHT +
            role_score * ROLE_WEIGHT +
            age_score * AGE_WEIGHT
        )
        
        match_scores.append({
            'user_id': user_id,
            'user_name': user_name,
            'matched_user_id': matched_id,
            'matched_user_name': matched_name,
            'final_score': round(final_score, 2),
            'location_score': round(location_score * 100, 2),
            'genre_score': round(genre_score * 100, 2),
            'audio_score': round(audio_score * 100, 2),
            'role_score': round(role_score * 100, 2),
            'age_score': round(age_score * 100, 2),
            'distance_km': meta_row['distance_km'],
            'genre_matches': meta_row['genre_matches'],
            'role_matches': meta_row['role_matches'],
            'age_compatible': meta_row['age_compatible'],
            'matched_location': meta_row['matched_location']
        })
    
    # Sort by final score descending and take top 10
    match_scores.sort(key=lambda x: x['final_score'], reverse=True)
    top_10 = match_scores[:10]
    
    # Add rank
    for rank, match in enumerate(top_10, 1):
        match['match_rank'] = rank
        consolidated_matches.append(match)
    
    print(f"  ✓ {user_name}: Top match = {top_10[0]['matched_user_name']} ({top_10[0]['final_score']:.2f})")

# --- Save consolidated matches ---
print(f"\n✅ Generated {len(consolidated_matches)} consolidated matches")

# Create DataFrame with desired column order
output_df = pd.DataFrame(consolidated_matches)
output_df = output_df[[
    'user_id', 'user_name', 'match_rank', 
    'matched_user_id', 'matched_user_name',
    'final_score', 'location_score', 'genre_score', 'audio_score', 'role_score', 'age_score',
    'distance_km', 'genre_matches', 'role_matches', 'age_compatible', 'matched_location'
]]

output_df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ Consolidated matches saved to {OUTPUT_CSV}")

# --- Print statistics ---
print("\n📊 Weighting used:")
print(f"   Location: {LOCATION_WEIGHT}%")
print(f"   Genre:    {GENRE_WEIGHT}%")
print(f"   Audio:    {AUDIO_WEIGHT}%")
print(f"   Role:     {ROLE_WEIGHT}%")
print(f"   Age:      {AGE_WEIGHT}%")
print(f"   Total:    {LOCATION_WEIGHT + GENRE_WEIGHT + AUDIO_WEIGHT + ROLE_WEIGHT + AGE_WEIGHT}%")
