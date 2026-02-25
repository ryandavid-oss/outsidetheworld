import os
import json
import re
import html

# --- RECALIBRATED PATHS ---
posts_folder = './blogger_posts/'
manifest_file = './manifest.json'
output_file = './wayback_purified.js'

def purify_signal():
    if not os.path.exists(manifest_file):
        print("Error: manifest.json not found in this directory.")
        return

    # Create folder if it doesn't exist (safety check)
    if not os.path.exists(posts_folder):
        print(f"Error: Folder '{posts_folder}' not found.")
        return

    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    purified_data = []

    print(f"Purifying {len(manifest)} blog signals from {posts_folder}...")

    for entry in manifest:
        # Match the filename from your manifest
        file_path = os.path.join(posts_folder, entry['file'])
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()

                # 1. Restore Punctuation and Strip HTML tags
                # We keep newlines to preserve the blog's structure
                clean_text = re.sub(r'<(p|br|div).*?>', '\n', content, flags=re.IGNORECASE)
                clean_text = re.sub(r'<[^<]+?>', '', clean_text)
                
                # The "Magic Wand" for 's, " ", etc.
                clean_text = html.unescape(clean_text)

                # 2. Package for AI Processing
                purified_data.append({
                    "file": entry['file'],
                    "current_title": entry['title'],
                    "year": entry['year'],
                    "date": entry['date'],
                    "raw_body": clean_text[:2500] # Grabbing more context for better titling
                })
            except Exception as e:
                print(f"Failed to read {entry['file']}: {e}")
        else:
            print(f"Warning: File {entry['file']} not found in {posts_folder}")

    # Save as a JS variable for easy transmission
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("const wayback_raw_dump = " + json.dumps(purified_data, indent=4) + ";")

    print(f"\nPurification complete.")
    print(f"Next Step: Upload '{output_file}' here.")

if __name__ == "__main__":
    purify_signal()