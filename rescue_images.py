import os
import shutil
import re

# --- CONFIGURATION ---
# 1. Path to where your Google Takeout / Blogger export is sitting
# Change this if you moved it, but usually it's in Downloads
search_source = os.path.expanduser('~/Downloads') 

# 2. Path to your current project's Hipsta folder
target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images', 'Hipsta')

print(f"🔦 Searching for missing Hipsta-history in: {search_source}")

# Create a list of all IDs we need from your .md files
needed_ids = set()
stories_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Stories')

for filename in os.listdir(stories_dir):
    if filename.endswith(".md"):
        with open(os.path.join(stories_dir, filename), 'r') as f:
            ids = re.findall(r'(\d{5,})', f.read())
            needed_ids.update(ids)

print(f"🎯 We are looking for {len(needed_ids)} unique image IDs.")

# Search the source folder and all sub-folders
found_count = 0
for root, dirs, files in os.walk(search_source):
    for file in files:
        # Check if the filename contains one of our IDs
        for photo_id in needed_ids:
            if photo_id in file:
                source_path = os.path.join(root, file)
                # Use '+' to match what the website expects
                safe_name = file.replace(' ', '+')
                dest_path = os.path.join(target_dir, safe_name)
                
                if not os.path.exists(dest_path):
                    shutil.copy2(source_path, dest_path)
                    found_count += 1
                break

print(f"✅ MISSION COMPLETE: Found and rescued {found_count} images.")
print("Now run 'python3 build_index.py' to finish the job!")