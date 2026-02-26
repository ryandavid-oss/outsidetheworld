import os
import json

# Detect the current folder
current_dir = os.path.dirname(os.path.abspath(__file__))
hipsta_images_dir = os.path.join(current_dir, 'Images', 'Hipsta')
manifest_path = os.path.join(current_dir, 'hipsta_manifest.json')

print("🕵️  ARCHIVE DIAGNOSTICS STARTING...")

# 1. Check Folder
if not os.path.exists(hipsta_images_dir):
    print(f"❌ ERROR: Cannot find folder at {hipsta_images_dir}")
    exit()

# 2. List actual files on your hard drive
actual_files = os.listdir(hipsta_images_dir)
print(f"📁 Found {len(actual_files)} images in /Images/Hipsta")

# 3. Check Manifest
if not os.path.exists(manifest_path):
    print("❌ ERROR: hipsta_manifest.json is missing!")
    exit()

with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"📑 Manifest contains {len(data)} entries.")

# 4. Compare
missing_count = 0
examples = []

for entry in data:
    # Get the filename from the path (e.g., 'My Photo.jpg')
    target_file = os.path.basename(entry['image'])
    
    if target_file not in actual_files:
        missing_count += 1
        if len(examples) < 5:
            # Check for common issues: Case sensitivity
            close_matches = [f for f in actual_files if f.lower() == target_file.lower()]
            issue = "Total Mismatch"
            if close_matches:
                issue = f"Case/Extension issue (Found '{close_matches[0]}')"
            
            examples.append(f"- '{target_file}' is missing. Issue: {issue}")

print(f"\n📊 RESULTS:")
print(f"✅ Working: {len(data) - missing_count}")
print(f"❌ Broken: {missing_count}")

if examples:
    print("\n🔍 EXAMPLES OF FAILURES:")
    for ex in examples:
        print(ex)

print("\n--- DIAGNOSTICS COMPLETE ---")