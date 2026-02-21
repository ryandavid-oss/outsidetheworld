import os
import re
import urllib.request

# SETTINGS
atom_file = 'feed.atom' # Make sure this file is in your project folder
target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images', 'Hipsta')

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

print("🌐 STARTING LIVE GOOGLE RESCUE...")

# 1. Read the atom file
with open(atom_file, 'r', encoding='utf-8') as f:
    atom_data = f.read()

# 2. Find all Image links and their IDs
# This regex looks for the s1600 (high res) links
image_links = re.findall(r'href="(https://blogger.googleusercontent.com/.*?/(.*?))"', atom_data)

download_count = 0
for link, filename in image_links:
    # Clean the filename (Google adds junk sometimes)
    clean_filename = filename.replace(' ', '+')
    save_path = os.path.join(target_dir, clean_filename)
    
    if not os.path.exists(save_path):
        try:
            print(f"📥 Downloading: {clean_filename}...")
            urllib.request.urlretrieve(link, save_path)
            download_count += 1
        except Exception as e:
            print(f"❌ Could not download {clean_filename}: {e}")

print(f"\n✅ SUCCESS: {download_count} images downloaded directly from Google.")
print("🔄 Running final sync to update your site...")

# 3. Update the manifest
import subprocess
subprocess.run(["python3", "build_index.py"])