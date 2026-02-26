import os
import json

# SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
hipsta_images_dir = os.path.join(current_dir, 'Images', 'Hipsta')
manifest_path = os.path.join(current_dir, 'hipsta_manifest.json')

print("🛠️  SYNCING MANIFEST TO ACTUAL HARD DRIVE FILENAMES...")

if not os.path.exists(hipsta_images_dir):
    print("❌ ERROR: Images folder not found!")
    exit()

# 1. Map every file on your drive by its lowercase name
actual_files = os.listdir(hipsta_images_dir)
discovery_map = {f.lower().replace(' ', '+'): f for f in actual_files if not f.startswith('.')}

with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

updated_count = 0
for entry in data:
    # Get the filename from the manifest
    target_filename = os.path.basename(entry['image']).lower()
    
    # Try to find the REAL filename on your hard drive
    if target_filename in discovery_map:
        real_filename = discovery_map[target_filename]
        new_path = f"Images/Hipsta/{real_filename}"
        
        if entry['image'] != new_path:
            entry['image'] = new_path
            updated_count += 1

# 2. Save the corrected manifest
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print(f"✅ SUCCESS: {updated_count} image paths corrected in the manifest.")
print("Refresh your browser now!")