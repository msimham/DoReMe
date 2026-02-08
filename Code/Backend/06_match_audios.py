import os
import pandas as pd
import librosa
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import subprocess

# --- Paths ---
CSV_PATH = "./Data/04_people_input_with_coords.csv"
CLIP_DIR = "./Data/06_clips"
EMBED_PATH = "./Data/06_clip_embeddings.npz"  # where embeddings will be saved
OUTPUT_CSV = "./Results/06_audio_user_matches.csv"  # output matches

# --- Normalization settings ---
SAMPLE_RATE = 22050  # Hz (librosa default)
MONO = True

# --- Load CSV ---
print("Loading CSV...")
df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded {len(df)} users\n")

# --- Step 1: Normalize clips ---
print("Normalizing clips...")
normalized_count = 0
for idx, row in df.iterrows():
    track_id = row.get("user_id") or row.get("youtube_video")
    clip_path = os.path.join(CLIP_DIR, f"{track_id}_clip.wav")
    if not os.path.exists(clip_path):
        continue

    # Use temporary file to avoid ffmpeg input/output conflict
    temp_path = clip_path + ".temp.wav"
    
    try:
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", clip_path,
            "-ac", "1",  # mono
            "-ar", str(SAMPLE_RATE),  # sample rate
            "-acodec", "pcm_s16le",  # 16-bit PCM
            temp_path
        ], check=True)
        
        # Replace original with normalized version
        os.replace(temp_path, clip_path)
        normalized_count += 1
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ Failed to normalize {clip_path}: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)

print(f"✅ Normalized {normalized_count} clips\n")

# --- Step 2: Generate embeddings using librosa ---
print("Generating audio embeddings with librosa (stable, no crashes)...\n")
embeddings = []
metadata = []

for idx, row in df.iterrows():
    track_id = row.get("user_id") or row.get("youtube_video")
    artist_name = f"{row.get('first_name','')} {row.get('last_name','')}".strip()
    clip_path = os.path.join(CLIP_DIR, f"{track_id}_clip.wav")

    if not os.path.exists(clip_path):
        continue

    try:
        # Load audio with librosa
        y, sr = librosa.load(clip_path, sr=SAMPLE_RATE, mono=MONO)
        
        if len(y) == 0:
            print(f"  ⚠ Empty audio: {artist_name}")
            continue

        # Extract robust audio features
        # 1. MFCCs (timbral texture) - most important
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        
        # 2. Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        
        # 3. Chroma (harmony)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        
        # 4. Rhythm features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
        else:
            tempo = float(tempo)
        
        # Combine features
        features = np.concatenate([
            mfcc_mean,
            mfcc_std,
            [np.mean(spectral_centroids), np.std(spectral_centroids)],
            [np.mean(spectral_rolloff), np.std(spectral_rolloff)],
            chroma_mean,
            [tempo]
        ])
        
        embeddings.append(features)
        metadata.append({
            "track_id": track_id,
            "artist_name": artist_name,
            "clip_path": clip_path
        })
        print(f"  ✓ {artist_name}")

    except Exception as e:
        print(f"  ✗ Failed: {artist_name} - {e}")

if len(embeddings) == 0:
    print("\n❌ No embeddings generated. Exiting.")
    exit(1)

print(f"\n✅ Generated {len(embeddings)} embeddings")

embeddings = np.stack(embeddings)
np.savez_compressed(EMBED_PATH, embeddings=embeddings, metadata=metadata)
print(f"\n✅ Embeddings saved to {EMBED_PATH}")

# --- Step 3: Calculate similarity and find top matches ---
print("\nCalculating audio similarity matches...")
sim_matrix = cosine_similarity(embeddings)

matches_data = []
for i, query_meta in enumerate(metadata):
    query_id = query_meta["track_id"]
    query_artist = query_meta["artist_name"]

    sims = sim_matrix[i]
    sorted_idxs = sims.argsort()[::-1]

    top_matches = []
    for idx in sorted_idxs:
        if metadata[idx]["track_id"] != query_id:
            top_matches.append(idx)
            if len(top_matches) >= 10:
                break

    match_record = {"user_id": query_id, "artist_name": query_artist}
    for rank, match_idx in enumerate(top_matches, 1):
        match_meta = metadata[match_idx]
        match_record[f"match_{rank}_user_id"] = match_meta["track_id"]
        match_record[f"match_{rank}_artist"] = match_meta["artist_name"]
        match_record[f"match_{rank}_score"] = round(float(sims[match_idx]), 4)

    matches_data.append(match_record)
    print(f"  ✓ {query_artist}: Found {len(top_matches)} matches")

# --- Step 4: Save results ---
matches_df = pd.DataFrame(matches_data)
matches_df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ Audio matches saved to {OUTPUT_CSV}")
print(f"   Total users matched: {len(matches_data)}")
