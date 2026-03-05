import os
import re

# --- CONFIGURATION ---
SOURCE_FOLDER = './Oldhtml'
OUTPUT_FOLDER = './Repaired'
NEW_IMG_PATH = 'Images/Legacy/' 

def global_prepend_repair():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # This regex looks for src="filename.ext" where there is NO folder path already there
    # It catches banner.jpg but ignores Images/Legacy/banner.jpg
    naked_src_pattern = re.compile(r'(src|href)=["\'](?!(?:https?://|/|Images/))([\w\-\.]+\.(?:jpg|jpeg|gif|png|ico|bmp))["\']', re.IGNORECASE)

    print(f"--- STARTING GLOBAL PREPEND SCAN ---")

    for file in os.listdir(SOURCE_FOLDER):
        if file.endswith((".html", ".htm")):
            file_path = os.path.join(SOURCE_FOLDER, file)
            output_path = os.path.join(OUTPUT_FOLDER, file)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Prepend the path to any naked filename found in an src or href
            new_content = naked_src_pattern.sub(rf'\1="{NEW_IMG_PATH}\2"', content)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"REPAIRED: {file}")

    print(f"\n--- SCAN COMPLETE ---")

if __name__ == "__main__":
    global_prepend_repair()