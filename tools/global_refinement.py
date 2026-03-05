import os
from bs4 import BeautifulSoup

# THE CONFIGURATION
META_TAGS = """
    <meta name="theme-color" content="#0a0a0a">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
"""

def refine_page(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1. INJECT SYSTEM BLACKOUT
    # Check for theme-color specifically to avoid double-injection
    if soup.head and not soup.find('meta', {'name': 'theme-color'}):
        # We parse the meta block and append it to the head
        head_fragment = BeautifulSoup(META_TAGS, 'html.parser')
        soup.head.append(head_fragment)

    # 2. STANDARDIZE EQUAL.SVG LOGO
    logos = soup.find_all('img', src=lambda x: x and 'Equal' in x)
    for logo in logos:
        # Check if already wrapped in our specific container
        parent = logo.parent
        if not (parent.name == 'div' and 'hero-logo-container' in parent.get('class', [])):
            container = soup.new_tag('div', attrs={'class': 'hero-logo-container'})
            logo.wrap(container)
            # Ensure the img has the hero-logo class for mobile scaling
            if 'hero-logo' not in logo.get('class', []):
                logo['class'] = logo.get('class', []) + ['hero-logo']

    # 3. ENSURE CURSOR DIVS EXIST
    if soup.body and not soup.find(id='cursor-ring'):
        # Insert at the very top of body so they don't interfere with layout
        ring = soup.new_tag('div', id='cursor-ring')
        dot = soup.new_tag('div', id='cursor-dot')
        soup.body.insert(0, dot)
        soup.body.insert(0, ring)

    # 4. SAVE WITH PRETTIFIED OUTPUT
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"Refined: {file_path}")

# Execute across all HTML files
for file in os.listdir('.'):
    if file.endswith('.html'):
        refine_page(file)