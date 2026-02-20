import os
import json

# The folder containing your markdown files
posts_folder = 'blogger_posts'
manifest_file = 'manifest.json'

residue_list = []

# Scan the folder for all .md files
for filename in os.listdir(posts_folder):
    if filename.endswith(".md"):
        # Expecting format: YYYY-MM-DD-title.md
        parts = filename.replace(".md", "").split("-")
        if len(parts) >= 4:
            year = parts[0]
            date = f"{parts[1]}/{parts[2]}"
            # Convert dashes back to spaces for the title display
            title = " ".join(parts[3:]).capitalize()
            
            residue_list.append({
                "year": year,
                "date": date,
                "title": title,
                "file": filename
            })

# Sort by date (newest first)
residue_list.sort(key=lambda x: x['file'], reverse=True)

# Save the manifest
with open(manifest_file, 'w') as f:
    json.dump(residue_list, f, indent=4)

print(f"Estate Synchronized. {len(residue_list)} entries found in the residue manifest.")