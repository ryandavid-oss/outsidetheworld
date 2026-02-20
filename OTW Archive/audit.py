import os

def audit_archive(path):
    print(f"--- Auditing Archive: {path} ---")
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/ ({len(files)} files)")
        
        # Just show the first few subdirectories to keep it clean
        if level > 2:
            continue

# Run this by typing 'python audit.py' in your VS Code terminal
audit_archive('.')