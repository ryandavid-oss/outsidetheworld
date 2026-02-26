import os

# SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(current_dir, 'Stories')

print("🖋️  BOLDING LENS AND FILM SPECS...")

count = 0
for filename in os.listdir(stories_dir):
    if filename.endswith(".md"):
        path = os.path.join(stories_dir, filename)
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Perform the replacements
        # We target the specific labels with their colons
        new_content = content.replace("Lens:", "**Lens:**")
        new_content = new_content.replace("Film:", "**Film:**")

        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            count += 1

print(f"✅ SUCCESS: Formatted specs in {count} story files.")