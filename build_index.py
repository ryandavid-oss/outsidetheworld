import os
import json
import re

# 1. FIND THE FOLDER (No matter what it's named)
current_dir = os.path.dirname(os.path.abspath(__file__))
target_folder = None

# Look for anything named 'stories' or 'Stories' or 'STORIES'
for folder in os.listdir(current_dir):
    if folder.lower() == 'stories' and os.path.isdir(os.path.join(current_dir, folder)):
        target_folder = folder
        break

if not target_folder:
    print("❌ ERROR: I still can't find a folder named 'Stories' here.")
    print(f"I am currently looking inside: {current_dir}")
else:
    stories_path = os.path.join(current_dir, target_folder)
    output_file = os.path.join(current_dir, 'hipsta_manifest.json')
    posts = []

    print(f"🔎 Found your folder: /{target_folder}")
    print("Scanning for artifacts...")

    # 2. INDEX THE FILES
    for filename in sorted(os.listdir(stories_path), reverse=True):
        if filename.endswith(".md"):
            filepath = os.path.join(stories_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find title and image
                title_match = re.search(r'^# (.*)', content)
                img_match = re.search(r'!\[.*\]\((.*)\)', content)
                
                posts.append({
                    "title": title_match.group(1) if title_match else "Untitled",
                    "image": img_match.group(1) if img_match else "Images/placeholder.jpg",
                    "file": f"{target_folder}/{filename}"
                })

    # 3. SAVE THE PACKING LIST
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=4)

    print(f"✅ SUCCESS: {len(posts)} artifacts indexed in hipsta_manifest.json")