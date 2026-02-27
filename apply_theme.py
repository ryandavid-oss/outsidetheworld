import os
import re

# We only target the "Core" hex codes that appear everywhere
CORE_HEX_MAP = {
    r'#6395EE': 'var(--brand-blue)',
    r'#A0BEF5': 'var(--brand-light-blue)',
    r'#91AFB3': 'var(--brand-teal)',
    # Standardizing all the various blacks (#000000, #020202) to the Core #050505
    r'#050505': 'var(--bg-dark)',
    r'#020202': 'var(--bg-dark)',
    r'#000000': 'var(--bg-dark)'
}

def gentle_uplink():
    print("--- STARTING GENTLE THEME UPLINK ---")
    
    for file in os.listdir('.'):
        if file.endswith('.html'):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            
            # 1. Add the Global Stylesheet Link if missing
            if 'theme.css' not in content:
                new_content = content.replace('</head>', '    <link rel="stylesheet" href="theme.css">\n</head>')

            # 2. Only replace the CORE colors
            for hex_code, var_name in CORE_HEX_MAP.items():
                new_content = re.sub(hex_code, var_name, new_content, flags=re.IGNORECASE)

            if new_content != content:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"UPLINKED: {file}")

    print("--- UPLINK COMPLETE. LOCAL OVERRIDES PRESERVED. ---")

if __name__ == "__main__":
    gentle_uplink()