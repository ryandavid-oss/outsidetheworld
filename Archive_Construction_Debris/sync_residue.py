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
            
# --- THE MASTER SQUISH ---
            raw_title = " ".join(parts[3:])
            
            # 1. Turn '39' back to apostrophe AND handle the missing ones
            # We look for " s " at the end of words that usually need it
            raw_title = raw_title.replace(" 39 s", "'s").replace("39 s", "'s").replace(" 39", "'")
            
            # 2. Specifically fix "it s" which I see in your screenshot
            raw_title = raw_title.replace("it s", "it's").replace("It s", "It's")
            
            # 3. Final Regex Squish: Find ANY space sitting before an apostrophe and KILL IT
            raw_title = re.sub(r'\s+\'', "'", raw_title)
            
            # 4. Collapse extra spaces
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