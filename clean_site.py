import os
import re

# THE GOAL: Strip scanlines, normalize body, and update the Atmospherics block.
def clean_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. REMOVE THE SCANLINES (background-image and size inside body)
    # This regex looks for the specific linear-gradient patterns we've been using.
    content = re.sub(r'background-image:\s*linear-gradient\(rgba\(18, 16, 16, 0\).*?\);', '', content, flags=re.DOTALL)
    content = re.sub(r'background-size:\s*100% 4px, 3px 100%;', '', content)

    # 2. REMOVE OLD ATMOSPHERICS BLOCK (body::after)
    # We look for the entire body::after block to replace it with a fresh one.
    content = re.sub(r'body::after\s*\{.*?\}(?=\s*nav|\s*/\*)', '', content, flags=re.DOTALL)

    # 3. PREPARE THE NEW "CLEAN" ATMOSPHERICS BLOCK
    # No stripes, just a very soft, high-end RGB wash.
    new_atmospherics = """
/* THE CLEAN ATMOSPHERIC WASH */
body::after {
    content: " "; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: radial-gradient(circle at 50% 50%, rgba(10, 10, 10, 0) 0%, rgba(0, 0, 0, 0.4) 100%),
                linear-gradient(90deg, rgba(255, 0, 0, 0.01), rgba(0, 255, 0, 0.005), rgba(0, 0, 255, 0.01));
    pointer-events: none; z-index: 3000; opacity: 0.2;
}
"""

    # 4. INJECT THE NEW BLOCK
    # We'll stick it right before the </style> tag.
    if '</style>' in content:
        content = content.replace('</style>', new_atmospherics + '\n    </style>')

    # 5. ENSURE BODY IS CLEAN
    # Make sure body has a solid blackout background.
    if 'background-color: var(--bg-dark);' not in content:
        content = content.replace('body {', 'body {\n    background-color: #0a0a0a;')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"--- Processed: {filepath}")

# EXECUTION
for filename in os.listdir('.'):
    if filename.endswith('.html'):
        clean_html_file(filename)

print("\\n[ RECLAMATION COMPLETE ]: The glass is clean. Scanlines purged.")