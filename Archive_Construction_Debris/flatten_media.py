import os
import shutil

# CONFIGURATION
# This is where your year/month folders are currently
SOURCE_DIR = 'Images/posts' 
# This is where we want them to all live together
TARGET_DIR = 'Images/Instagram' 

def flatten_media():
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Error: {SOURCE_DIR} not found.")
        return

    os.makedirs(TARGET_DIR, exist_ok=True)
    count = 0

    print("⚙️  Flattening the media maze...")

    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4')):
                source_path = os.path.join(root, file)
                target_path = os.path.join(TARGET_DIR, file)
                
                # Copy to the new flat folder
                shutil.copy2(source_path, target_path)
                count = 1

    print(f"✅ Success! {count} images unified in {TARGET_DIR}")

if __name__ == "__main__":
    flatten_media()