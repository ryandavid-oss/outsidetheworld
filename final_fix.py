import os
import json

# SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
hipsta_images_dir = os.path.join(current_dir, 'Images', 'Hipsta')
manifest_path = os.path.join(current_dir, 'hipsta_manifest.json')

print("🕵️  STARTING FINAL DEEP-CLEAN ALIGNMENT...")

if not os.path.exists(manifest_path):
    print("❌ ERROR: hipsta_manifest.json not found. Run build_index.py first!")
    exit()

with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest_data = json.load(f)

# 1. Map out what we actually have on the hard drive (Case-Insensitive)
actual_files = os.listdir(hipsta_images_dir)
files_lowercase_map = {f.lower(): f for f in actual_files if not f.startswith('.')}

rename_count = 0
missing_text_only = 0

for entry in manifest_data:
    target_path = entry['image'] # e.g., "Images/Hipsta/photo-727669.JPG"
    target_filename = os.path.basename(target_path)
    
    if target_filename == "placeholder.jpg":
        missing_text_only += 1
        continue

    # If the file isn't found exactly as named...
    if target_filename not in actual_files:
        # Check if it exists with a different case (e.g., .jpg vs .JPG)
        if target_filename.lower() in files_lowercase_map:
            old_name = files_lowercase_map[target_filename.lower()]
            
            old_path = os.path.join(hipsta_images_dir, old_name)
            new_path = os.path.join(hipsta_images_dir, target_filename)
            
            os.rename(old_path, new_path)
            # Update map so we don't try to use the old name again
            del files_lowercase_map[target_filename.lower()]
            rename_count += 1

print(f"\n📊 FINAL REPORT:")
print(f"✅ Renamed {rename_count} files to fix case/extension issues.")
print(f"📝 Found {missing_text_only} posts that are text-only (No image exists).")

# 2. FINAL INDEX UPDATE
print("\n🔄 Refreshing the index one last time...")
import subprocess
subprocess.run(["python3", "build_index.py"])

print("\n--- ALL SYSTEMS ALIGNED. CHECK FLOTSAM.HTML NOW! ---")