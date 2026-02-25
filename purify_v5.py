import os
import json
import re

# --- CONFIG ---
posts_folder = './blogger_posts/'
output_file = './wayback_purified.js'

def goldilocks_purify():
    if not os.path.exists(posts_folder):
        print(f"Error: Folder {posts_folder} not found.")
        return

    purified_data = []
    files = [f for f in os.listdir(posts_folder) if f.endswith('.md')]

    print(f"Refining {len(files)} files for optimal spacing...")

    for filename in files:
        file_path = os.path.join(posts_folder, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 2:
                continue

            # 1. Extract Title & Date
            title = lines[0].replace('#', '').strip()
            date_line = lines[1].replace('Date:', '').strip()
            year = date_line.split(",")[-1].strip() if "," in date_line else "Unknown"

            # 2. Extract Body and Clean Spacing
            body_content = "".join(lines[2:]).strip()
            
            # Clean "Invisible" HTML spaces (nbsp) that cause weird gaps
            body_content = body_content.replace('\xa0', ' ').replace('&nbsp;', ' ')
            
            # Reduce "Aggressive" Spacing: 
            # This regex replaces 3 or more newlines with exactly 2 newlines.
            body_content = re.sub(r'\n{3,}', '\n\n', body_content)

            purified_data.append({
                "file": filename,
                "year": year,
                "date": date_line,
                "title": title,
                "body": body_content
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    purified_data.sort(key=lambda x: (x['year'], x['file']), reverse=True)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("const wayback_raw_dump = " + json.dumps(purified_data, indent=4) + ";")

    print(f"Success. Check '{output_file}' for the refined experience.")

if __name__ == "__main__":
    goldilocks_purify()