import xml.etree.ElementTree as ET
import os
import re
import json

# SETTINGS
ATOM_FILE = 'feed.atom'
OUTPUT_DIR = 'Stories/Favorites'
MANIFEST_FILE = 'favorites_manifest.json'

# Namespaces for Blogger Atom feeds
ns = {
    'atom': 'http://www.w3.org/2005/Atom',
    'blogger': 'http://schemas.google.com/blogger/2018'
}

def clean_html(raw_html):
    """Removes the mobile-photo block and cleans HTML tags."""
    # Remove the photo wrapper
    clean = re.sub(r'<p class="mobile-photo">.*?</p>', '', raw_html, flags=re.DOTALL)
    # Remove all other tags
    clean = re.sub(r'<[^>]+>', '\n', clean)
    # Fix common entities
    clean = clean.replace('&amp;#39;', "'").replace('&amp;quot;', '"').strip()
    return clean

def extract_data():
    if not os.path.exists(ATOM_FILE):
        print(f"❌ Error: {ATOM_FILE} not found in this folder.")
        return

    tree = ET.parse(ATOM_FILE)
    root = tree.getroot()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    entries_list = []

    for entry in root.findall('atom:entry', ns):
        # Only process Posts and Pages
        etype = entry.find('blogger:type', ns)
        if etype is None or etype.text not in ['POST', 'PAGE']:
            continue

        title = entry.find('atom:title', ns).text or "Untitled"
        published = entry.find('atom:published', ns).text[:10]
        content_html = entry.find('atom:content', ns).text or ""

        # Extract the image URL
        img_match = re.search(r'src="([^"]+)"', content_html)
        image_url = img_match.group(1) if img_match else ""

        # Clean the text body
        body_text = clean_html(content_html)

        # Create a safe filename
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title)
        file_path = f"{OUTPUT_DIR}/{safe_title}.md"

        # Write the Markdown file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n")
            f.write(f"## {published}\n\n")
            if image_url:
                f.write(f"![{title}]({image_url})\n\n")
            f.write(body_text)

        # Add to manifest list
        entries_list.append({
            "title": title,
            "date": published,
            "image": image_url,
            "file": file_path
        })

    # Sort manifest chronologically
    entries_list.sort(key=lambda x: x['date'])

    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries_list, f, indent=4)

    print(f"✅ Success! Recovered {len(entries_list)} items into {OUTPUT_DIR}")
    print(f"✅ Manifest created: {MANIFEST_FILE}")

if __name__ == "__main__":
    extract_data()