import os
import json
from datetime import datetime, timedelta

# Settings
posts_folder = 'blogger_posts'
manifest_file = 'manifest.json'

# ARIZONA TIME SYNC
az_time = datetime.utcnow() - timedelta(hours=7)
current_date_str = az_time.strftime("%Y-%m-%d")

residue_list = []

# THE LOOP: Scans every file in your blogger_posts folder
for filename in os.listdir(posts_folder):
    if filename.endswith(".md"):
        # Expecting format: YYYY-MM-DD-title.md
        parts = filename.replace(".md", "").split("-")
        
        if len(parts) >= 4:
            year = parts[0]
            date = f"{parts[1]}/{parts[2]}"
            
            # --- THE SURGICAL TITLE CLEANER ---
            # 1. Join the remaining parts with spaces
            raw_title = " ".join(parts[3:])
            
            # 2. Kill the "39" and the spaces around it specifically
            # This turns "theodore roosevelt 39 s lake" into "theodore roosevelt's lake"
            raw_title = raw_title.replace(" 39 s", "'s").replace(" 39 ", "'").replace("39 s", "'s")
            
            # 3. Catch instances where a space might still exist before an apostrophe
            raw_title = raw_title.replace(" 's", "'s")
            
            # 4. Final polish: remove double spaces and capitalize only the first word
            # This 'split/join' trick collapses any weird gaps left behind
            title = " ".join(raw_title.split()).capitalize()
            
            residue_list.append({
                "year": year,
                "date": date,
                "title": title,
                "file": filename
            })

# Sort by filename (newest first)
residue_list.sort(key=lambda x: x['file'], reverse=True)

# Save the updated manifest
with open(manifest_file, 'w') as f:
    json.dump(residue_list, f, indent=4)

print(f"Estate Synchronized for Arizona Time. {len(residue_list)} entries found.")