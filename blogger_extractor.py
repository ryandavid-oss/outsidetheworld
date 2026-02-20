import os
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime

ATOM_FILE = "feed.atom"
OUTPUT_DIR = "Blogger_Posts"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def clean_content_with_spacing(raw_html):
    if raw_html is None: return ""
    html_str = str(raw_html)
    
    # 1. Convert structural tags to newlines BEFORE stripping them
    # This turns </div> or <br> into a real line break the computer can see
    html_str = re.sub(r'<(br|br\s*/|/p|/div|/h[1-6])>', '\n', html_str, flags=re.IGNORECASE)
    
    # 2. Now strip all HTML except for <img> tags
    clean = re.sub(r'<(?!img|/img)[^>]+>', '', html_str)
    
    # 3. Fix the HTML symbols (like &#39;)
    return html.unescape(clean).strip()

def extract_posts():
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    try:
        tree = ET.parse(ATOM_FILE)
        root = tree.getroot()
        count = 0

        for entry in root.findall('atom:entry', ns):
            try:
                title_node = entry.find('atom:title', ns)
                title = str(title_node.text) if (title_node is not None and title_node.text is not None) else "Untitled"
                
                pub_node = entry.find('atom:published', ns)
                if pub_node is None or pub_node.text is None: continue
                
                published = pub_node.text
                dt = datetime.strptime(published[:10], '%Y-%m-%d')
                date_str = dt.strftime('%B %d, %Y')
                file_date = dt.strftime('%Y-%m-%d')

                content_node = entry.find('atom:content', ns)
                body_html = content_node.text if (content_node is not None and content_node.text is not None) else ""
                
                # USE THE NEW SPACING CLEANER HERE
                body_text = clean_content_with_spacing(body_html)
                    
                if len(body_text) < 40: continue

                safe_title = re.sub(r'[^a-zA-Z0-9]', '-', title)[:30]
                file_name = f"{file_date}-{safe_title}.md"
                
                with open(os.path.join(OUTPUT_DIR, file_name), 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n")
                    f.write(f"Date: {date_str}\n\n")
                    f.write(body_text)
                
                count += 1
            except:
                continue

        print(f"\n--- FORMATTING & IMAGES RECOVERED ---")
        print(f"Re-processed {count} posts with proper spacing.")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    extract_posts()