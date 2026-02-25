import os
import json
import re
import html # Crucial for punctuation recovery

folder_path = os.path.dirname(os.path.abspath(__file__)) 
output_file = os.path.join(folder_path, 'poetry_data.js')

# Pattern for dates, but we'll manually filter the "2009" fake date
date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b|\b(?:Winter|Spring|Summer|Fall)\s+\d{4}\b|\b\d{4}\b'

poems_archive = []

print(f"Purifying signals in: {folder_path}")

for filename in os.listdir(folder_path):
    if filename.endswith(".html") or filename.endswith(".htm"):
        try:
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()

                # 1. Capture Title
                title_match = re.search(r'<h1.*?>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else filename.replace('.html', '').upper()
                title = html.unescape(re.sub('<[^<]+?>', '', title))

                # 2. Extract Body and Restore Punctuation
                body_raw = re.sub(r'<(p|br|div).*?>', '\n', content, flags=re.IGNORECASE)
                body_raw = re.sub(r'<[^<]+?>', '', body_raw)
                body_raw = html.unescape(body_raw) # RESTORES IT'S, DON'T, ETC.

                # 3. Signature Cut-off
                if "RyanDavid Burningham" in body_raw:
                    body_raw = body_raw.split("RyanDavid Burningham")[0]

                # 4. Filter out "Outside The World" from the top of the poem
                body_raw = body_raw.replace("Outside The World", "").strip()

                # 5. Date Logic: Ignore "23 March 2009"
                dates_found = re.findall(date_pattern, body_raw)
                extracted_date = "[DATE_LOST]"
                
                bad_date = "23 March 2009"
                valid_dates = [d for d in dates_found if bad_date not in d and "2009" not in d]
                
                if valid_dates:
                    extracted_date = valid_dates[0]
                elif dates_found and bad_date not in dates_found[0]:
                    extracted_date = dates_found[0]

                # 6. Final Clean and Preserve Shape
                lines = [line.strip() for line in body_raw.splitlines()]
                # Remove title if it's the first line
                if lines and (title.lower() in lines[0].lower() or not lines[0]):
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

with open(output_file, 'w', encoding='utf-8') as out:
    out.write("const archive = " + json.dumps(poems_archive, indent=4) + ";")

print(f"Success. {len(poems_archive)} verses purified into poetry_data.js")