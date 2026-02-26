import os, json, re

# --- CONFIG ---
input_folder = 'current_narrative'
output_file = 'narrative_data.js'

def sync_production():
    posts = []
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    files = [f for f in os.listdir(input_folder) if f.endswith('.md')]
    print(f"UPLINK_SYNC: Processing {len(files)} entries...")

    for filename in files:
        file_path = os.path.join(input_folder, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 2:
                continue

            # 1. Target the top two lines specifically
            # Line 0 is the Title, Line 1 is the Date
            title = lines[0].replace('#', '').strip()
            date_str = lines[1].replace('Date:', '').replace('###', '').strip()

            # 2. Preserve EVERYTHING from line 2 (the 3rd line) onward
            # This keeps your spacing, your poems, and your formatting intact
            body_content = "".join(lines[2:]).strip()

            posts.append({
                "title": title,
                "date": date_str,
                "body": body_content,
                "file": filename
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Sort: Newest filename (YYYY-MM-DD) first
    posts.sort(key=lambda x: x['file'], reverse=True)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"const current_narrative = {json.dumps(posts, indent=4)};")
    
    print(f"SUCCESS: {len(posts)} entries synced with preserved spacing.")

if __name__ == "__main__":
    sync_production()