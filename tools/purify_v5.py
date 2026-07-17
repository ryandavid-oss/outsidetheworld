import os
import json
import re
import hashlib

# --- CONFIG ---
# Ensure these match your actual folder names in GitHub
posts_folder = 'blogger_posts' 
output_file = 'wayback_purified.js'

# Public builds must never republish records whose source-name hash is listed here.
PRIVATE_SOURCE_HASHES = {
    "e83d7bbca16ee63b2efbb00e906e5395a144c1131a649f84ae39c38d04ccbfe5",
}
FORCE_REFRESH_SOURCE_HASHES = {
    "829d2474e4238de680e0e934cd14b8a048dbcdaf29348269752e04f5dca17e13",
    "47e95bfa927e7d2cf3a45c87c15735d974d70e9518abf04028b47c980808e3e4",
    "08252d75137f0bd0afef8dd5796e943a8cd770671a660fd0f6713d3a98de13eb",
    "c02be764287ae4f162ffd3f64d0005a2f4a2b3727d35e2a2b9a85d8f1a0d87fd",
    "0a221125d29a67b5f8a6c5af162eb68166d7dfb1ec38927d6824daea1b163da6",
    "78ce4981b4bf9dfcacd82f782490f376f18b345a93ee3c6240de5860663084d1",
}


def is_public_source(filename):
    digest = hashlib.sha256(filename.encode("utf-8")).hexdigest()
    return digest not in PRIVATE_SOURCE_HASHES


def load_curated_entries():
    if not os.path.exists(output_file):
        return {}
    try:
        with open(output_file, 'r', encoding='utf-8') as source:
            text = source.read()
        records = json.loads(text[text.index('['):text.rindex(']') + 1])
        return {
            str(record.get('file')): record
            for record in records
            if isinstance(record, dict) and record.get('file')
        }
    except (OSError, ValueError, json.JSONDecodeError):
        return {}

def goldilocks_purify():
    # 1. BOT-CHECK: Create folder if it's missing (prevents crash)
    if not os.path.exists(posts_folder):
        print(f"SIGNAL_LOST: {posts_folder} folder not found. Creating empty dir.")
        os.makedirs(posts_folder)
        # We stop here because there's nothing to process
        return

    purified_data = []
    
    # 2. FILE-CHECK: Look for .md files
    files = [
        f for f in os.listdir(posts_folder)
        if f.endswith('.md') and is_public_source(f)
    ]
    
    if not files:
        print("EMPTY_FEED: No markdown files found in the posts folder.")
        return

    print(f"PROCESSING_BATCH: {len(files)} entries found.")

    curated_entries = load_curated_entries()

    for filename in files:
        file_path = os.path.join(posts_folder, filename)
        source_hash = hashlib.sha256(filename.encode("utf-8")).hexdigest()
        if filename in curated_entries and source_hash not in FORCE_REFRESH_SOURCE_HASHES:
            purified_data.append(curated_entries[filename])
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 2:
                print(f"SKIPPING: {filename} (File too short or malformed)")
                continue

            # 1. Extract Title & Date
            title = lines[0].replace('#', '').strip()
            date_line = lines[1].replace('Date:', '').strip()
            
            # Simple Year Fallback
            year = "2026"
            if "," in date_line:
                year = date_line.split(",")[-1].strip()

            # 2. Extract Body and Clean Spacing
            body_content = "".join(lines[2:]).strip()
            
            # Clean "Invisible" HTML spaces (nbsp)
            body_content = body_content.replace('\xa0', ' ').replace('&nbsp;', ' ')
            
            # Reduce Aggressive Spacing (Limit to 2 breaks)
            body_content = re.sub(r'\n{3,}', '\n\n', body_content)

            purified_data.append({
                "file": filename,
                "year": year,
                "date": date_line,
                "title": title,
                "body": body_content
            })
        except Exception as e:
            print(f"CRITICAL_ERROR on {filename}: {e}")

    # 3. SORT: Newest Year, Newest File Name (so 2026 appears before 2002)
    purified_data.sort(key=lambda x: (x['year'], x['file']), reverse=True)

    # 4. WRITE: Update the JS Uplink file
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("const wayback_raw_dump = " + json.dumps(purified_data, indent=4) + ";")

    print(f"UPLINK_SUCCESS: {len(purified_data)} entries stored in {output_file}")

if __name__ == "__main__":
    goldilocks_purify()
