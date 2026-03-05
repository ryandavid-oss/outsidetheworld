import os
import re
import shutil

# --- CONFIGURATION ---
SOURCE_FOLDER = './Oldhtml'      # Where your old pages are
OUTPUT_FOLDER = './Repaired'    # Where the fixed versions go
NEW_IMG_PATH = 'Images/Legacy/' # The unified image home

def safe_repair():
    # Ensure output folder exists
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    asset_pattern = re.compile(r'(src|href|background)=["\'](.*?/)?([\w\-\.]+\.(jpg|jpeg|png|gif|bmp|ico))["\']', re.IGNORECASE)

    print(f"--- STARTING SAFE REPAIR ---")

    for file in os.listdir(SOURCE_FOLDER):
        if file.endswith((".html", ".htm")):
            file_path = os.path.join(SOURCE_FOLDER, file)
            output_path = os.path.join(OUTPUT_FOLDER, file)
            
            # Read from Source
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Repair the links
            new_content = asset_pattern.sub(rf'\1="{NEW_IMG_PATH}\3"', content)

            # Write to Output (Original is untouched)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"DONE: {file} -> Moved to {OUTPUT_FOLDER}")

    print(f"--- MISSION COMPLETE. CHECK THE '{OUTPUT_FOLDER}' FOLDER. ---")

if __name__ == "__main__":
    safe_repair()