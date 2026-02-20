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

# Scan the folder for all .md files
for filename in os.listdir(posts_folder):
    if filename.endswith(".md"):
        # Expecting format: YYYY-MM-DD-title.md
        parts = filename.replace(".md", "").split("-")
        
        if len(parts) >= 4:
            year = parts[0]
            date = f"{parts[1]}/{parts[2]}"
            
            # --- THE FIX FOR TITLES ---
            # 1. Join the remaining parts
            raw_title = " ".join(parts[3:])
            
            # 2. Specifically catch common number-sanitization (like 39 for apostrophe)
            # This regex looks for " 39 " or " 39s " and turns it back into 's
            raw_title = raw_title.replace(" 39 s", "'s").replace(" 39 ", "'")
            
            # 3. Capitalize the first letter only
            title = raw_title.capitalize()
            
            residue_list.append({
                "year": year,
                "date": date,
                "title": title,
                "file": filename
            })

# Sort by filename (newest first)
residue_list.sort(key=lambda x: x['file'], reverse=True)

with open(manifest_file, 'w') as f:
    json.dump(residue_list, f, indent=4)

print(f"Estate Synchronized. {len(residue_list)} entries found.")