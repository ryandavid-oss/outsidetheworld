import os
import json

# SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
hipsta_images_dir = os.path.join(current_dir, 'Images', 'Hipsta')

print("🚀 STARTING MASTER ARCHIVE ALIGNMENT...")

if not os.path.exists(hipsta_images_dir):
    print(f"❌ ERROR: Cannot find folder at {hipsta_images_dir}")
    exit()

# 1. FIX THE FILES ON DISK
actual_files = os.listdir(hipsta_images_dir)
rename_count = 0

for filename in actual_files:
    # Skip hidden system files
    if filename.startswith('.'): continue
    
    # Standardize: Replace spaces with '+' to match the Blogger/Markdown links
    new_name = filename.replace(' ', '+')
    
    # Handle Case sensitivity (Common in Blogger .JPG vs .jpg)
    # We will keep the original extension case but match the + sign logic
    if new_name != filename:
        old_path = os.path.join(hipsta_images_dir, filename)
        new_path = os.path.join(hipsta_images_dir, new_name)
        
        # Avoid overwriting if file already exists
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            rename_count += 1

print(f"✅ Renamed {rename_count} images to match archive links.")

# 2. RE-RUN THE INDEXER LOGIC
print("🔄 Updating manifest...")
import subprocess
try:
    # This runs your existing build_index.py automatically
    subprocess.run(["python3", "build_index.py"], check=True)
    print("✅ Manifest updated successfully.")
except:
    print("⚠️  Could not run build_index.py automatically. Please run it manually!")

print("\n--- ALIGNMENT COMPLETE. REFRESH YOUR BROWSER! ---")