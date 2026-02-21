import os
import re
import json

# SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(current_dir, 'Stories')
images_dir = os.path.join(current_dir, 'Images', 'Hipsta')
manifest_path = os.path.join(current_dir, 'hipsta_manifest.json')

print("🎯 STARTING NUMERIC ID ALIGNMENT...")

# 1. Map every image on your hard drive by its numeric ID
# Example: 'image-727669.jpeg' becomes ID '727669'
actual_images = os.listdir(images_dir)
id_map = {}
for img in actual_images:
    # Find any 6-digit or longer number in the filename
    match = re.search(r'(\d{5,})', img)
    if match:
        id_map[match.group(1)] = img

# 2. Fix the Markdown stories
fix_count = 0
for filename in os.listdir(stories_dir):
    if filename.endswith(".md"):
        path = os.path.join(stories_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the image link and extract the number
        img_match = re.search(r'\(Images/Hipsta/.*?-?(\d{5,})\.(jpg|jpeg|png|JPG)\)', content)
        if img_match:
            photo_id = img_match.group(1)
            if photo_id in id_map:
                real_filename = id_map[photo_id]
                new_content = re.sub(r'\(Images/Hipsta/.*?\)', f'(Images/Hipsta/{real_filename})', content)
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fix_count += 1

print(f"✅ Repaired {fix_count} image links in your Story files.")

# 3. Re-run the Indexer
print("🔄 Updating manifest...")
import subprocess
subprocess.run(["python3", "build_index.py"])

print("\n--- RECLAMATION COMPLETE. REFRESH FLOTSAM! ---")