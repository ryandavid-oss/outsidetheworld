import os
import json
import re
from datetime import datetime, timedelta

# Settings
posts_folder = 'blogger_posts'
manifest_file = 'manifest.json'

az_time = datetime.utcnow() - timedelta(hours=7)
current_date_str = az_time.strftime("%Y-%m-%d")

residue_list = []

for filename in os.listdir(posts_folder):
    if filename.endswith(".md"):
        parts = filename.replace(".md", "").split("-")
        
        if len(parts) >= 4:
            year = parts[0]
            date = f"{parts[1]}/{parts[2]}"
            
            # --- THE REGEX CLEANER ---
            raw_title = " ".join(parts[3:])
            
            # 1. Turn '39' back into an apostrophe
            raw_title = raw_title.replace("39", "'")
            
            # 2. THE SQUISH: This finds any space followed by an apostrophe
            # and removes just the space.
            raw_title = re.sub(r'\s+\'', "'", raw_title)
            
            # 3. Clean up any accidental double spaces or trailing bits
            title = " ".join(raw_title.split()).capitalize()
            
            residue_list.append({
                "year": year,
                "date": date,
                "title": title,
                "file": filename
            })

residue_list.sort(key=lambda x: x['file'], reverse=True)

with open(manifest_file, 'w') as f:
    json.dump(residue_list, f, indent=4)

print(f"Estate Synchronized. {len(residue_list)} entries found.")