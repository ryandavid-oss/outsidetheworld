import os
import json
import re

# Targeting exactly where this script lives
folder_path = os.path.dirname(os.path.abspath(__file__)) 
output_file = os.path.join(folder_path, 'poetry_data.js')

poems_archive = []

# Regex for common date patterns (e.g., "January 1, 2001", "Winter 2002", "2001")
date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b|\b(?:Winter|Spring|Summer|Fall)\s+\d{4}\b|\b\d{4}\b'

print(f"Refining extraction in: {folder_path}")

for filename in os.listdir(folder_path):
    if filename.endswith(".html") or filename.endswith(".htm"):
        try:
            # Use 'utf-8-sig' to handle potential Windows/Mac encoding quirks with punctuation
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()

                # 1. Capture the Title
                title_match = re.search(r'<h1.*?>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
                if not title_match:
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                
                title = title_match.group(1).strip() if title_match else filename.replace('.html', '').replace('_', ' ').upper()
                title = re.sub('<[^<]+?>', '', title)

                # 2. Extract Body Text & Handle Delimiters
                # We strip the HTML tags first but keep line breaks
                body_raw = re.sub(r'<(p|br|div).*?>', '\n', content, flags=re.IGNORECASE)
                body_raw = re.sub(r'<[^<]+?>', '', body_raw) # Remove all other tags

                # --- SIGNATURE CUT-OFF ---
                # We find your name and ignore everything after it
                signature = "RyanDavid Burningham"
                if signature in body_raw:
                    body_raw = body_raw.split(signature)[0]

                # 3. Harvest the Date
                # Look for a date in the body before we clean it too much
                dates_found = re.findall(date_pattern, body_raw)
                extracted_date = dates_found[0] if dates_found else "[DATE_LOST]"

                # 4. Final Cleanup (Preserving apostrophes and stanzas)
                lines = [line.strip() for line in body_raw.splitlines()]
                # Filter out the title if it appears at the top of the body
                if lines and title.lower() in lines[0].lower():
                    lines = lines[1:]
                
                body_clean = "\n".join([line for line in lines if line])

                poems_archive.append({
                    "title": title,
                    "date": extracted_date,
                    "location": "[ORIGIN_UNKNOWN]",
                    "body": body_clean
                })
        except Exception as e:
            print(f"Error in {filename}: {e}")

# Write to the JS data file
with open(output_file, 'w', encoding='utf-8') as out:
    out.write("const archive = " + json.dumps(poems_archive, indent=4) + ";")

print(f"Refinement complete. {len(poems_archive)} signals purified.")