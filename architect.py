import os
import re
from collections import defaultdict

POSTS_DIR = "Blogger_Posts"
OUTPUT_FILE = "wayback.html"

def generate_wayback():
    posts_by_year = defaultdict(list)

   # 1. Gather all posts and group by year
    for filename in sorted(os.listdir(POSTS_DIR), reverse=True):
        if filename.endswith(".md"):
            year = filename[:4]
            with open(os.path.join(POSTS_DIR, filename), 'r') as f:
                title = f.readline().replace('# ', '').strip()
            
            # --- THE CLEANUP FILTER ---
            # This skips "Untitled" posts and anything too short to be a real entry
            if title.lower() == "untitled" or not title:
                continue 
            
            posts_by_year[year].append({
                "title": title,
                "file": filename,
                "date": filename[5:10].replace('-', '/')
            })

    # 2. Build the HTML
    years = sorted(posts_by_year.keys(), reverse=True)
    year_nav = "".join([f'<button class="year-btn" onclick="showYear(\'{y}\')">{y}</button>' for y in years])
    
    content_sections = ""
    for year in years:
        post_links = "".join([
            f'<div class="archive-item"><span>{p["date"]}</span><a href="post.html?file={p["file"]}">{p["title"]}</a></div>'
            for p in posts_by_year[year]
        ])
        content_sections += f'<div id="year-{year}" class="year-section" style="display:none;">{post_links}</div>'

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Wayback | Outside The World</title>
    <style>
        body {{ background: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; margin: 0; padding: 5%; }}
        .nav-logo {{ height: 50px; margin-bottom: 40px; }}
        h1 {{ font-family: 'Georgia', serif; font-size: 3rem; color: white; margin-bottom: 10px; }}
        .year-picker {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 40px 0; border-bottom: 1px solid #222; padding-bottom: 20px; }}
        .year-btn {{ background: none; border: 1px solid #333; color: #888; padding: 8px 15px; cursor: pointer; transition: 0.3s; font-weight: 700; }}
        .year-btn:hover, .year-btn.active {{ border-color: #91AFB3; color: white; background: rgba(145,175,179,0.1); }}
        .archive-item {{ padding: 15px 0; border-bottom: 1px solid #111; display: flex; gap: 20px; align-items: baseline; }}
        .archive-item span {{ font-family: monospace; color: #91AFB3; font-size: 0.9rem; }}
        .archive-item a {{ color: #ccc; text-decoration: none; font-size: 1.2rem; transition: 0.2s; }}
        .archive-item a:hover {{ color: white; padding-left: 10px; }}
        .back-link {{ text-decoration: none; color: #91AFB3; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; }}
    </style>
</head>
<body>
    <a href="personal.html" class="back-link">← Back to Journal</a>
    <h1>The Wayback</h1>
    <p style="color: #666;">Twenty-six years of digital residue, sorted by era.</p>

    <div class="year-picker">{year_nav}</div>
    <div id="archive-content">{content_sections}</div>

    <script>
        function showYear(year) {{
            document.querySelectorAll('.year-section').forEach(s => s.style.display = 'none');
            document.querySelectorAll('.year-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('year-' + year).style.display = 'block';
            event.target.classList.add('active');
        }}
        // Show the latest year by default
        showYear('{years[0]}');
    </script>
</body>
</html>
"""
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html_template)
    print(f"Wayback page created successfully: {{OUTPUT_FILE}}")

if __name__ == "__main__":
    generate_wayback()