import os
import re

# --- CONFIGURATION ---
SOURCE_FOLDER = './Oldhtml'      # Your original vintage files
OUTPUT_FOLDER = './Repaired'    # The "Fixed" versions
NEW_IMG_PATH = 'Images/Legacy/' # Where you moved the images

def deep_repair():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # This regex is much more aggressive. 
    # It finds path-like strings (../../pics/ etc) that end in image extensions.
    # It works inside HTML tags AND JavaScript strings.
    deep_pattern = re.compile(r'([\'"/])?([\w\-\./]+)/([\w\-\.]+\.(jpg|jpeg|png|gif|bmp|ico|svg))', re.IGNORECASE)

    print(f"--- STARTING DEEP SCAN: {SOURCE_FOLDER} ---")

    for file in os.listdir(SOURCE_FOLDER):
        if file.endswith((".html", ".htm")):
            file_path = os.path.join(SOURCE_FOLDER, file)
            output_path = os.path.join(OUTPUT_FOLDER, file)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # REPAIR LOGIC:
            # It replaces any directory path it finds with our new flat path.
            # Example: '../../pics/buttonD.jpg' -> 'Images/Legacy/buttonD.jpg'
            new_content = deep_pattern.sub(rf'\1{NEW_IMG_PATH}\3', content)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"RECOVERY SUCCESS: {file}")

    print(f"\n--- MISSION COMPLETE ---")
    print(f"All files in '{OUTPUT_FOLDER}' are now pointing to {NEW_IMG_PATH}")

if __name__ == "__main__":
    deep_repair()