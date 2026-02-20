import os
import json
from datetime import datetime, timedelta

# Settings
posts_folder = 'blogger_posts'
manifest_file = 'manifest.json'

# --- THE ARIZONA FIX ---
# This ensures that even if a file is uploaded without a date, 
# the script knows it's currently UTC-7 in Arizona
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
            # Convert dashes back to spaces for the title
            title = " ".join(parts[3:]).capitalize()
            
            residue_list.append({
                "year": year,
                "date": date,
                "title": title,
                "file": filename
            })

# Sort by filename (newest first based on the date prefix)
residue_list.sort(key=lambda x: x['file'], reverse=True)

# Save the manifest
with open(manifest_file, 'w') as f:
    json.dump(residue_list, f, indent=4)

print(f"Estate Synchronized for Arizona Time. {len(residue_list)} entries found.")