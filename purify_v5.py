import os
import json
import re

# --- CONFIG ---
# Ensure these match your actual folder names in GitHub
posts_folder = 'blogger_posts' 
output_file = 'wayback_purified.js'

def goldilocks_purify():
    # 1. BOT-CHECK: Create folder if it's missing (prevents crash)
    if not os.path.exists(posts_folder):
        print(f"SIGNAL_LOST: {posts_folder} folder not found. Creating empty dir.")
        os.makedirs(posts_folder)
        # We stop here because there's nothing to process
        return

    purified_data = []
    
    # 2. FILE-CHECK: Look for .md files
    files = [f for f in os.listdir(posts_folder) if f.endswith('.md')]
    
    if not files:
        print("EMPTY_FEED: No markdown files found in the posts folder.")
        return

    print(f"PROCESSING_BATCH: {len(files)} entries found.")

    for filename in files:
        file_path = os.path.join(posts_folder, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 2:
                print(f"SKIPPING: {filename} (File too short or malformed)")
                continue

            # 1. Extract Title & Date
            title = lines[0].replace('#', '').strip()
            date_line = lines[1].replace('Date:', '').strip()
            
            # Simple Year Fallback
            year = "2026"
            if "," in date_line:
                year = date_line.split(",")[-1].strip()

            # 2. Extract Body and Clean Spacing
            body_content = "".join(lines[2:]).strip()
            
            # Clean "Invisible" HTML spaces (nbsp)
            body_content = body_content.replace('\xa0', ' ').replace('&nbsp;', ' ')
            
            # Reduce Aggressive Spacing (Limit to 2 breaks)
            body_content = re.sub(r'\n{3,}', '\n\n', body_content)

            purified_data.append({
                "file": filename,
                "year": year,
                "date": date_line,
                "title": title,
                "body": body_content
            })
        except Exception as e:
            print(f"CRITICAL_ERROR on {filename}: {e}")

    # 3. SORT: Newest Year, Newest File Name (so 2026 appears before 2002)
    purified_data.sort(key=lambda x: (x['year'], x['file']), reverse=True)

    # 4. WRITE: Update the JS Uplink file
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("const wayback_raw_dump = " + json.dumps(purified_data, indent=4) + ";")

    print(f"UPLINK_SUCCESS: {len(purified_data)} entries stored in {output_file}")

if __name__ == "__main__":
    goldilocks_purify()