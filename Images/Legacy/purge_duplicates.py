import os
import re

TARGET_FOLDER = './Images/Legacy'

def sanitize_filenames():
    if not os.path.exists(TARGET_FOLDER):
        print("Folder not found.")
        return

    print(f"--- SANITIZING FILENAMES IN {TARGET_FOLDER} ---")
    
    for filename in os.listdir(TARGET_FOLDER):
        # 1. Replace spaces and special chars with underscores
        # 2. Convert to lowercase for consistency
        new_name = re.sub(r'[^a-zA-Z0-9\.]', '_', filename).lower()
        # Clean up double underscores
        new_name = re.sub(r'_{2,}', '_', new_name)

        if new_name != filename:
            old_path = os.path.join(TARGET_FOLDER, filename)
            new_path = os.path.join(TARGET_FOLDER, new_name)
            
            # Check if target exists to avoid overwriting
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"[RENAMED]: {filename} -> {new_name}")
            else:
                print(f"[SKIPPED]: {new_name} already exists.")

    print("--- FILENAMES SANITIZED ---")

if __name__ == "__main__":
    sanitize_filenames()