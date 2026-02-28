import os

# This script looks specifically for the '+' vs ' ' mismatch
current_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(current_dir, 'Stories')

if not os.path.exists(stories_dir):
    print("❌ Error: Move this script into your project folder next to /Stories")
else:
    print("Repairing image links...")
    count = 0
    for filename in os.listdir(stories_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(stories_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # The Fix: Replace '+' with a space in the image links
            if "Images/Hipsta/" in content:
                new_content = content.replace('+', ' ')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1

    print(f"✅ SUCCESS: Repaired {count} story links. Now re-run your indexer!")