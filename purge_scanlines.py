import os
import re

def purge_redundant_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. REMOVE SCANLINE GRADIENTS (Inside the body tag)
    # This targets the multi-line background-image and background-size rules
    content = re.sub(r'background-image:\s*linear-gradient\(rgba\(18, 16, 16, 0\).*?\);', '', content, flags=re.DOTALL)
    content = re.sub(r'background-size:\s*100% 4px, 3px 100%;', '', content)

    # 2. REMOVE THE ENTIRE body::after BLOCK
    # Since theme.css now handles the vignette, this block is just dead weight.
    # This regex finds "body::after" and everything until the next closing brace.
    content = re.sub(r'body::after\s*\{.*?\}(?=\s*nav|\s*/\*|\s*header|\s*\n)', '', content, flags=re.DOTALL)

    # 3. CLEAN UP EXTRA WHITESPACE
    # Sometimes deleting CSS leaves awkward double-newlines; this tidies it up.
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"--- Purged: {filepath}")

# EXECUTION LOOP
html_files = [f for f in os.listdir('.') if f.endswith('.html')]

if not html_files:
    print("No HTML files found in the current directory.")
else:
    for filename in html_files:
        purge_redundant_css(filename)
    print("\n[ PURGE COMPLETE ]: Redundant scanlines and atmospherics removed.")