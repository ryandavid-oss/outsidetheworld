import os

POSTS_DIR = "Blogger_Posts"

def cleanup_comments():
    count = 0
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".md"):
            path = os.path.join(POSTS_DIR, filename)
            with open(path, 'r') as f:
                first_line = f.readline()
                
            if "# Untitled" in first_line:
                os.remove(path)
                count += 1
                
    print(f"Janitor complete: Scrubbed {count} reader comments from the archive.")

if __name__ == "__main__":
    cleanup_comments()