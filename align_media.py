import json
import os
import re

# The manifests identified in your survey
manifests = ['insta_manifest.json', 'hipsta_manifest.json', 'favorites_manifest.json']

def align_paths():
    for m_file in manifests:
        if os.path.exists(m_file):
            print(f"--- ALIGNING: {m_file} ---")
            with open(m_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changes_made = 0
            for entry in data:
                # Instagram uses 'path' or 'uri' - we check both
                key = 'path' if 'path' in entry else 'uri' if 'uri' in entry else None
                
                if key:
                    original = entry[key]
                    
                    # 1. Fix Unicode/Instagram Encoding (e.g., \u0026 to &)
                    # Python's json.load handles most, but let's ensure literal consistency
                    cleaned = original.encode().decode('unicode-escape') if '\\u' in original else original
                    
                    # 2. Normalize to local project root
                    # Strip any "up-directory" or absolute path gunk
                    cleaned = cleaned.replace('../', '').replace('//', '/')
                    
                    # 3. Ensure it starts with 'media/' 
                    # (since that's where we just copied everything)
                    if 'media/' in cleaned:
                        # Find where 'media/' starts and keep everything after it
                        cleaned = cleaned[cleaned.find('media/'):]
                    elif not cleaned.startswith('media/'):
                        # If it just says "posts/img.jpg", make it "media/posts/img.jpg"
                        cleaned = 'media/' + cleaned.lstrip('/')

                    if original != cleaned:
                        entry[key] = cleaned
                        changes_made += 1
            
            with open(m_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"SUCCESS: {changes_made} paths updated in {m_file}.\n")
        else:
            print(f"SKIP: {m_file} not found in root.")

if __name__ == "__main__":
    align_paths()