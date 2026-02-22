import os
import re
import json
from html import unescape

POSTS_FILE = 'posts_1.html'
COMMENTS_FILE = 'post_comments.html'
OUTPUT_DIR = 'Stories/Instagram'
MANIFEST_FILE = 'insta_manifest.json'
# We are now pointing to the clean flattened folder
IMAGE_BASE_PATH = 'Images/Instagram' 

def final_sync():
    # 1. BUILD COMMENT LIBRARY
    comment_library = {}
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            c_entries = re.findall(r'Comment<div><div>(.*?)</div></div>.*?Media Owner<div><div>(.*?)</div></div>.*?Time<div><div>(.*?)</div></div>', f.read(), re.DOTALL)
            for text, user, timestamp in c_entries:
                date_match = re.search(r'([A-Z][a-z]{2}\s\d{1,2},\s20\d{2})', timestamp)
                if date_match:
                    d_key = date_match.group(1)
                    if d_key not in comment_library: comment_library[d_key] = []
                    comment_library[d_key].append({"user": unescape(user).strip(), "text": unescape(text).strip()})

    # 2. PROCESS POSTS
    with open(POSTS_FILE, 'r', encoding='utf-8') as f:
        blocks = f.read().split('<div class="pam _3-95 _2ph- _a6-g uiBoxWhite noborder">')
    
    final_manifest = []
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, block in enumerate(blocks[1:]):
        # Grab the filename only, ignoring the old year/month folders
        img_match = re.search(r'src="media/posts/[^"]+/([^"]+)"', block)
        if not img_match: continue
        
        filename = img_match.group(1)
        new_img_path = f"{IMAGE_BASE_PATH}/{filename}"
        
        cap_match = re.search(r'<div class="_3-95 _2pim _a6-h _a6-i">(.*?)</div>', block, re.DOTALL)
        caption = unescape(cap_match.group(1)).strip() if cap_match else ""
        
        date_match = re.search(r'([A-Z][a-z]{2}\s\d{1,2},\s20\d{2})', block)
        post_date = date_match.group(1) if date_match else "Unknown Date"

        dialogue_md = ""
        if post_date in comment_library:
            dialogue_md = "\n\n---\n### DIALOGUE\n"
            for c in comment_library[post_date]:
                dialogue_md += f"**{c['user']}**: {c['text']}  \n"

        file_path = f"{OUTPUT_DIR}/insta_{i}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {post_date}\n\n![Post]({new_img_path})\n\n{caption}{dialogue_md}")

        final_manifest.append({"title": post_date, "date": post_date, "image": new_img_path, "file": file_path})

    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_manifest, f, indent=4)
    print(f"✅ FINAL SYNC COMPLETE. {len(final_manifest)} artifacts ready.")

if __name__ == "__main__":
    final_sync()