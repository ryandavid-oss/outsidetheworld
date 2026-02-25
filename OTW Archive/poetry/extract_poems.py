import os
import json
import re
import html

folder_path = os.path.dirname(os.path.abspath(__file__)) 
output_file = os.path.join(folder_path, 'poetry_data.js')

# The ghost date to be purged
BAD_DATE_SIGNAL = "23 March 2009"

poems_archive = []

print(f"Executing Legacy Extraction: {folder_path}")

for filename in os.listdir(folder_path):
    if filename.endswith(".html") or filename.endswith(".htm"):
        try:
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()

                # 1. Body Extraction & Punctuation Restoration
                body_raw = re.sub(r'<(p|br|div).*?>', '\n', content, flags=re.IGNORECASE)
                body_raw = re.sub(r'<[^<]+?>', '', body_raw)
                body_raw = html.unescape(body_raw)

                # 2. Surgical Stripping
                # Remove the signature and everything after it
                if "RyanDavid Burningham" in body_raw:
                    body_raw = body_raw.split("RyanDavid Burningham")[0]
                
                # Remove the ghost date and branding
                body_raw = body_raw.replace(BAD_DATE_SIGNAL, "")
                body_raw = body_raw.replace("Outside The World", "")
                
                # 3. Shape Cleanup
                lines = [line.strip() for line in body_raw.splitlines() if line.strip()]
                
                # 4. Data Packaging
                # We leave 'title' as the filename for now so YOU can approve the AI titles later
                poems_archive.append({
                    "id": filename.replace('.html', ''),
                    "suggested_title": "PENDING_AI_ANALYSIS", 
                    "original_filename": filename,
                    "body": "\n".join(lines)
                })
        except Exception as e:
            print(f"Signal Interrupted in {filename}: {e}")

with open(output_file, 'w', encoding='utf-8') as out:
    out.write("const raw_poetry_dump = " + json.dumps(poems_archive, indent=4) + ";")

print(f"Success. {len(poems_archive)} raw verses staged for AI Titling.")