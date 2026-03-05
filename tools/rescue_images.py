import os
import re
import urllib.request

# --- CONFIG ---
posts_dir = './blogger_posts/'
image_dir = './images/archive/'

# Create the folder if it doesn't exist
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

def rescue_mission():
    print("STARTING_RESCUE_PROTOCOL...")
    
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(posts_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find Blogger image URLs (regex matches the src="url" pattern)
            urls = re.findall(r'src="(https://blogger.googleusercontent.com/img/b/[^"]+)"', content)
            
            if urls:
                print(f"\nScanning {filename}: Found {len(urls)} images.")
                for url in urls:
                    # Create a clean filename from the URL
                    img_name = url.split('/')[-1]
                    if '?' in img_name: img_name = img_name.split('?')[0]
                    if not img_name.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                        img_name += '.jpg'
                    
                    local_path = os.path.join(image_dir, img_name)
                    
                    # Download the image using built-in urllib
                    try:
                        print(f"  -> Downloading: {img_name}")
                        # Adding a User-Agent header so Google doesn't block the request
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
                            out_file.write(response.read())
                        
                        # Update the Markdown content to use the LOCAL path
                        # We use a relative path so it works on GitHub and locally
                        content = content.replace(url, f'images/archive/{img_name}')
                    except Exception as e:
                        print(f"  !! FAILED to rescue: {url} | Error: {e}")

                # Save the updated Markdown file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

    print("\nRESCUE_COMPLETE. Your archive is now autonomous.")

if __name__ == "__main__":
    rescue_mission()