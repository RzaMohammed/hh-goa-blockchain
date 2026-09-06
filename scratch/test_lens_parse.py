import requests, io, re, json

with open('input/cropped_face_query.jpg', 'rb') as f:
    b = f.read()

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

r = s.post('https://lens.google.com/v3/upload', files={'encoded_image': ('face.jpg', io.BytesIO(b), 'image/jpeg')}, allow_redirects=True, timeout=12)

html = r.text
print("Final URL:", r.url)
print("Length:", len(html))

# Let's search for matches in google lens response
# Google visual matches often contain data-item-id, or AF_initDataCallback, or json blobs
callbacks = re.findall(r'AF_initDataCallback\((.*?)\);', html, re.DOTALL)
print("AF callbacks:", len(callbacks))

# Search for any image links (encrypted-tbn or external)
img_links = re.findall(r'(https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)[^\s"\'<>]*)', html)
print("Found img links:", len(img_links))

# Search for hrefs
hrefs = re.findall(r'href="([^"]+)"', html)
external_links = [h for h in hrefs if h.startswith('http') and 'google.com' not in h]
print("External links:", len(external_links))
if external_links:
    for h in external_links[:10]:
        print("Ext:", h)

# Search for AF_initDataCallback with ds:
for i, cb in enumerate(callbacks):
    if 'http' in cb:
        print(f"Callback {i} has http, length {len(cb)}")
        # Look for image URLs or page links
        found_urls = re.findall(r'https?://[^\s"\'\\]+', cb)
        print(f"Callback {i} URLs:", len(found_urls))
        for u in found_urls[:5]:
            print("  ->", u)
