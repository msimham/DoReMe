import pandas as pd
import subprocess
import os
import hashlib
import shutil

CSV_PATH = "./Data/04_people_input_with_coords.csv"
WAV_DIR = "./Data/wavs"
CLIP_DIR = "./Data/clips"
TMP_DIR = "./Data/tmp"

CLIP_START = 30   # seconds
CLIP_LEN = 10     # seconds

os.makedirs(WAV_DIR, exist_ok=True)
os.makedirs(CLIP_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

print(f"Reading CSV from {CSV_PATH}...")
df = pd.read_csv(CSV_PATH)

def safe_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:10]

for idx, row in df.iterrows():
    url = row.get("youtube_video")

    if pd.isna(url) or not str(url).strip():
        print(f"Skipping row {idx} (no YouTube link)")
        continue

    track_id = (
        row["user_id"]
        if "user_id" in row and pd.notna(row["user_id"])
        else safe_id(url)
    )

    artist_name = f"{row.get('first_name','')} {row.get('last_name','')}".strip()

    final_wav = os.path.join(WAV_DIR, f"{track_id}.wav")
    clip_path = os.path.join(CLIP_DIR, f"{track_id}_clip.wav")
    tmp_out = os.path.join(TMP_DIR, f"{track_id}.%(ext)s")

    if os.path.exists(clip_path):
        print(f"Skipping {artist_name} ({track_id}) - already processed")
        continue

    print(f"\nProcessing {artist_name} ({track_id})")
    print(f"  Source: {url}")

    try:
        # 1️⃣ Download first valid audio item
        subprocess.run(
            [
                "yt-dlp",
                "--yes-playlist",
                "--ignore-errors",
                "--extract-audio",
                "--audio-format", "wav",
                "--playlist-items", "1",
                "-o", tmp_out,
                url
            ],
            check=True
        )

        # Find downloaded WAV
        wav_files = [f for f in os.listdir(TMP_DIR) if f.startswith(track_id) and f.endswith(".wav")]
        if not wav_files:
            print(f"No WAV produced for {artist_name}")
            continue

        tmp_wav = os.path.join(TMP_DIR, wav_files[0])
        shutil.move(tmp_wav, final_wav)

        # 2️⃣ Trim clip
        print(f"  Creating {CLIP_LEN}s clip at {CLIP_START}s")
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", final_wav,
                "-ss", str(CLIP_START),
                "-t", str(CLIP_LEN),
                clip_path
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print(f"  ✓ Success")

    except subprocess.CalledProcessError as e:
        print(f"yt-dlp/ffmpeg failed for {artist_name}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Cleanup
shutil.rmtree(TMP_DIR, ignore_errors=True)

print("\n✓ Processing complete")
print(f"  WAVs  → {WAV_DIR}")
print(f"  Clips → {CLIP_DIR}")
