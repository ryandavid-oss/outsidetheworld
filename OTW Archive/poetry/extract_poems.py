import os
import json
import re

# This line tells Python to look exactly in the folder where the script is saved
folder_path = os.path.dirname(os.path.abspath(__file__)) 
output_file = os.path.join(folder_path, 'poetry_data.js')

poems_archive = []

print(f"Targeting Extraction: {folder_path}")

for filename in os.listdir(folder_path):
    # Skip the script itself and the output file
    if filename.endswith(".html") or filename.endswith(".htm"):
        try:
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # 1. Title Extraction
                title_match = re.search(r'<h1.*?>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
                if not title_match:
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                
                title = title_match.group(1).strip() if title_match else filename.replace('.html', '').replace('_', ' ').upper()
                title = re.sub('<[^<]+?>', '', title) # Clean tags from title

                # 2. Body Extraction (Targeting the actual poem content)
                body_match = re.search(r'<body.*?>(.*?)</body>', content, re.IGNORECASE | re.DOTALL)
                body_raw = body_match.group(1) if body_match else content
                
                # 3. Preservation of rhythmic line breaks
                # We turn <p>, <br>, and <div> into newlines to keep the poem's shape
                body_clean = re.sub(r'<(p|br|div).*?>', '\n', body_raw, flags=re.IGNORECASE)
                body_clean = re.sub(r'<[^<]+?>', '', body_clean) # Strip all other HTML noise
                
                # Clean up excessive whitespace but keep single line breaks
                body_clean = os.linesep.join([s.strip() for s in body_clean.splitlines() if s.strip()])

                poems_archive.append({
                    "title": title,
                    "date": "[RECOVERED_SIGNAL]",
                    "location": "[ORIGIN_UNKNOWN]",
                    "body": body_clean
                })
        except Exception as e:
            print(f"Error in {filename}: {e}")

# Save the clean data
with open(output_file, 'w', encoding='utf-8') as out:
    out.write("const archive = " + json.dumps(poems_archive, indent=4) + ";")

print(f"Success. {len(poems_archive)} verses extracted into poetry_data.js")