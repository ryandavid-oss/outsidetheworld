import os, json

# CONFIG
input_folder = 'current_narrative'
output_file = 'narrative_data.js'

def sync():
    print(f"--- STARTING SYNC ---")
    
    # 1. Ensure folder exists
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"NOTICE: Created missing folder: {input_folder}")

    # 2. List everything in the directory for the logs
    all_contents = os.listdir('.')
    print(f"ROOT_CONTENTS: {all_contents}")
    
    proj_contents = os.listdir(input_folder)
    print(f"FOLDER_CONTENTS ({input_folder}): {proj_contents}")

    # 3. Process files
    posts = []
    for filename in proj_contents:
        if filename.endswith('.md'):
            print(f"PROCESSING: {filename}")
            try:
                with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        posts.append({
                            "title": lines[0].replace('#', '').strip(),
                            "date": lines[1].replace('Date:', '').strip(),
                            "body": "".join(lines[2:]).strip(),
                            "file": filename
                        })
            except Exception as e:
                print(f"ERROR reading {filename}: {e}")

    # 4. Sort newest first
    posts.sort(key=lambda x: x['file'], reverse=True)

    # 5. THE GUARANTEED WRITE
    # We use 'w+' to ensure it truncates and writes fresh
    with open(output_file, 'w+', encoding='utf-8') as out:
        json_data = json.dumps(posts, indent=4)
        out.write(f"const current_narrative = {json_data};")
    
    print(f"SUCCESS: Wrote {len(posts)} posts to {output_file}")
    print(f"--- SYNC COMPLETE ---")

if __name__ == "__main__":
    sync()