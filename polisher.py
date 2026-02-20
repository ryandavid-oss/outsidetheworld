import os
import re

POSTS_DIR = "Blogger_Posts"

def polish_text(text):
    # 1. Split into 'Header' (Title/Date) and 'Body'
    parts = text.split('\n\n', 1)
    if len(parts) < 2: return text
    header, body = parts[0], parts[1]

    # 2. Remove 'Hard Wraps': Join lines that don't end in punctuation
    # This turns "per se, \n more of an" into "per se, more of an"
    body = re.sub(r'(?<![.!?])\n(?!\n)', ' ', body)

    # 3. Collapse multiple blank lines into exactly TWO newlines
    body = re.sub(r'\n\s*\n+', '\n\n', body)
    
    return f"{header}\n\n{body.strip()}"

def run_polish():
    count = 0
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".md"):
            path = os.path.join(POSTS_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            polished = polish_text(content)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(polished)
            count += 1
    print(f"Done! Polished {count} posts. Check 'Bagel Date' now!")

if __name__ == "__main__":
    run_polish()