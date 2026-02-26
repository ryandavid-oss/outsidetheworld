import os

def survey_root():
    # Get the current directory
    root = os.getcwd()
    
    print(f"\n--- SYSTEM_MANIFEST: {root} ---")
    
    # Separate folders and files for readability
    items = os.listdir(root)
    folders = [f for f in items if os.path.isdir(f) and not f.startswith('.')]
    files = [f for f in items if os.path.isfile(f) and not f.startswith('.')]
    
    print("\n[DIRECTORIES]")
    for folder in sorted(folders):
        print(f"  / {folder}")
        
    print("\n[FILES]")
    for file in sorted(files):
        # Add a little size info so you know what's heavy
        size = os.path.getsize(file) / 1024
        print(f"  - {file:<25} ({size:.1f} KB)")
    
    print("\n--- END_OF_MANIFEST ---")

if __name__ == "__main__":
    survey_root()