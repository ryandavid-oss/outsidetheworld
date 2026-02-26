import os
import re
import urllib.request

# SETTINGS
atom_file = 'feed.atom'
target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images', 'Hipsta')

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

print("🌐 STARTING SURGICAL GOOGLE RESCUE...")

# 1. Read the atom file
with open(atom_file, 'r', encoding='utf-8') as f:
    atom_data = f.read()

# 2. Find only the actual URL part (stops at the first double quote)
# This regex searches for the Google image domain and captures until it hits "
image_links = re.findall(r'href="(https://blogger.googleusercontent.com/[^"]+)"', atom_data)

download_count = 0
for link in image_links:
    # Get just the final filename from the URL
    full_filename = link.split('/')[-1]
    
    # Clean filenames: No spaces, and remove the '-h' if it exists
    clean_filename = full_filename.replace(' ', '+').replace('-h', '')
    
    save_path = os.path.join(target_dir, clean_filename)
    
    if not os.path.exists(save_path):
        try:
            print(f"📥 Downloading: {clean_filename}...")
            # Use a standard browser header to avoid 403 errors
            req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
                out_file.write(response.read())
            download_count += 1
        except Exception as e:
            # We skip errors for links that aren't actually images
            pass

print(f"\n✅ SUCCESS: {download_count} new images rescued.")

# 3. Update the index
import subprocess
subprocess.run(["python3", "build_index.py"])