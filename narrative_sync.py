import os, json

def diagnostic_sync():
    print("--- DIAGNOSTIC START ---")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # List EVERYTHING so we can see where we are
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}[{os.path.basename(root)}/]")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

    # The actual sync logic (extremely aggressive)
    posts = []
    target = 'current_narrative'
    
    # Look for the folder anywhere
    for root, dirs, files in os.walk('.'):
        if target in dirs:
            folder_path = os.path.join(root, target)
            print(f"!!! TARGET FOUND AT: {folder_path}")
            for filename in os.listdir(folder_path):
                if filename.endswith('.md'):
                    with open(os.path.join(folder_path, filename), 'r') as f:
                        lines = f.readlines()
                        posts.append({"title": lines[0], "date": "Synced", "body": "".join(lines[1:])})
    
    with open('narrative_data.js', 'w') as out:
        out.write(f"const current_narrative = {json.dumps(posts)};")
    print("--- DIAGNOSTIC END ---")

if __name__ == "__main__":
    diagnostic_sync()