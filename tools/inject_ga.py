import os

# Your specific Google Analytics Tag
GA_TAG = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-YKRKPFV2MB"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-YKRKPFV2MB');
</script>"""

def update_html_files():
    # Walk through the current directory and all subdirectories
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Safety check: Don't add the tag if it's already there
                if "G-YKRKPFV2MB" in content:
                    print(f"Skipping: {file_path} (Tag already exists)")
                    continue

                # Locate the <head> tag
                if "<head>" in content.lower():
                    # We use a case-insensitive replace to find <head>
                    # and insert the tag immediately after it.
                    new_content = content.replace("<head>", f"<head>\n{GA_TAG}", 1)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated: {file_path}")
                else:
                    print(f"Warning: No <head> tag found in {file_path}")

if __name__ == "__main__":
    print("Starting Google Analytics injection...")
    update_html_files()
    print("Finished!")