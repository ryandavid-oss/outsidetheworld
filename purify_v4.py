import os
import json

# --- CONFIG ---
posts_folder = './blogger_posts/'
output_file = './wayback_purified.js'

def markdown_purify():
    if not os.path.exists(posts_folder):
        print(f"Error: Folder {posts_folder} not found.")
        return

    purified_data = []
    files = [f for f in os.listdir(posts_folder) if f.endswith('.md')]

    print(f"Processing {len(files)} Markdown files...")

    for filename in files:
        file_path = os.path.join(posts_folder, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 2:
                continue

            # 1. Extract Title (Line 1: # Title)
            title = lines[0].replace('#', '').strip()

            # 2. Extract Date (Line 2: Date: Month Day, Year)
            date_line = lines[1].replace('Date:', '').strip()
            
            # Split the date to get the year for the sidebar filter
            # Assumes format: "December 12, 2003"
            year = "Unknown"
            if "," in date_line:
                year = date_line.split(",")[-1].strip()

            # 3. Extract Body (Everything from line 3 onwards)
            # We join the lines back together to preserve literal newlines
            body = "".join(lines[2:]).strip()

            purified_data.append({
                "file": filename,
                "year": year,
                "date": date_line,
                "title": title,
                "body": body
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Sort by year (descending) and then file name (descending) to keep order
    purified_data.sort(key=lambda x: (x['year'], x['file']), reverse=True)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("const wayback_raw_dump = " + json.dumps(purified_data, indent=4) + ";")

    print(f"Uplink Successful. {len(purified_data)} entries stored in '{output_file}'.")

if __name__ == "__main__":
    markdown_purify()