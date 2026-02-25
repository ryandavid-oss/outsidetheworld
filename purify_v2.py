import os
import json
import re
import html

# --- CONFIG ---
posts_folder = './blogger_posts/'
manifest_file = './manifest.json'
output_file = './wayback_purified.js'

def precision_purify():
    if not os.path.exists(manifest_file):
        print("Error: manifest.json not found.")
        return

    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    purified_data = []

    print(f"Restoring {len(manifest)} blog entries with images and punctuation...")

    for entry in manifest:
        file_path = os.path.join(posts_folder, entry['file'])
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()

                # 1. Decode HTML entities (Fixes the gaps in 's, ", etc.)
                clean_content = html.unescape(content)

                # 2. Preserve <img> tags but strip Blogger's messy <div> and <span> gunk
                # We keep line breaks and paragraph starts
                clean_content = re.sub(r'<(?!img|br|p|/p|b|i|em|strong|/b|/i|/em|/strong)[^>]+>', '', clean_content)
                
                # 3. Title Restoration (Auto-capitalize and clean up)
                raw_title = entry['title'].strip()
                display_title = raw_title.capitalize()
                # Add punctuation logic: if it ends in a word, add a period if missing
                if display_title and display_title[-1].isalnum():
                    # We won't force it, but we'll clean extra spaces
                    display_title = display_title.strip()

                purified_data.append({
                    "file": entry['file'],
                    "year": entry['year'],
                    "date": entry['date'],
                    "title": display_title,
                    "body": clean_content.strip()
                })
            except Exception as e:
                print(f"Error processing {entry['file']}: {e}")

    # Save to the JS file
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("const wayback_raw_dump = " + json.dumps(purified_data, indent=4) + ";")

    print(f"Uplink Successful. Images and punctuation restored in '{output_file}'.")

if __name__ == "__main__":
    precision_purify()