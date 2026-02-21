import os
import re
import urllib.request

# SETTINGS
atom_file = 'feed.atom'
target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images', 'Hipsta')

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

print("🌐 STARTING CLEAN GOOGLE RESCUE...")

# 1. Read the atom file
with open(atom_file, 'r', encoding='utf-8') as f:
    atom_data = f.read()

# 2. Find all Image links
# This regex specifically captures the final part of the URL as the filename
image_links = re.findall(r'href="(https://blogger.googleusercontent.com/.*?/([^/]+))"', atom_data)

download_count = 0
for link, full_filename in image_links:
    # CLEANING: Strip any weird Google suffixes like '-h' from the end
    # This ensures we get a clean .jpg filename
    clean_filename = full_filename.split('?')[0].replace(' ', '+')
    if '-h/' in clean_filename: clean_filename = clean_filename.split('/')[-1]
    
    save_path = os.path.join(target_dir, clean_filename)
    
    if not os.path.exists(save_path):
        try:
            print(f"📥 Downloading: {clean_filename}...")
            # We add a 'User-Agent' so Google doesn't block the automated download
            req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
                out_file.write(response.read())
            download_count += 1
        except Exception as e:
            print(f"❌ Could not download {clean_filename}: {e}")

print(f"\n✅ SUCCESS: {download_count} images rescued.")

# 3. Update the index
import subprocess
subprocess.run(["python3", "build_index.py"])