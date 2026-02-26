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
                content = f.read()

            # 1. Extract Title (First line with #)
            title_match = re.search(r'^#\s*(.*)', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else "Untitled Entry"

            # 2. Extract Date (Line starting with Date: or ###)
            date_match = re.search(r'(?:Date:|###)\s*(.*)', content)
            date_str = date_match.group(1).strip() if date_match else "Unknown Date"

            # 3. Clean Body (Remove the title and date lines so they don't double up)
            body = content
            body = re.sub(r'^#.*', '', body, count=1, flags=re.MULTILINE) # Remove title
            body = re.sub(r'(?:Date:|###).*', '', body, count=1)          # Remove date line
            body = body.strip()

            posts.append({
                "title": title,
                "date": date_str,
                "body": body,
                "file": filename
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Sort: Newest filename (YYYY-MM-DD) first
    posts.sort(key=lambda x: x['file'], reverse=True)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"const current_narrative = {json.dumps(posts, indent=4)};")
    
    print(f"SUCCESS: {len(posts)} entries synced to {output_file}")

if __name__ == "__main__":
    sync_production()