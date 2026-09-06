import requests, io, re, json, urllib.parse

with open('input/cropped_face_query.jpg', 'rb') as f:
    b = f.read()

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

# Test Bing visual search endpoint
files_data = {
    'imageBin': ('face.jpg', io.BytesIO(b), 'image/jpeg'),
}
r1 = s.post('https://www.bing.com/images/search?view=detailv2&iss=sbiupload&FORM=SBIHMP', files=files_data, allow_redirects=True, timeout=12)
html = r1.text

print(f"Status: {r1.status_code}, Length: {len(html)}")

# Find m= or similar attributes
m_list = re.findall(r'm="([^"]+)"', html)
print(f"m= count: {len(m_list)}")
if m_list:
    for item in m_list[:3]:
        try:
            from html import unescape
            d = json.loads(unescape(item))
            print("Sample m data:", d.get('murl'), d.get('purl'), d.get('t'))
        except Exception as e:
            print("Error parsing m:", e)

# Find imgurl= or mediaurl=
media_matches = re.findall(r'mediaurl=([^&"\'>\s]+)', html)
print(f"mediaurl count: {len(media_matches)}")
if media_matches:
    for m in media_matches[:3]:
        print("Sample mediaurl:", urllib.parse.unquote(m))

# Find json blobs with visual results
visual_search_data = re.findall(r'var\s+(?:imgData|feedData|data)\s*=\s*(\{.+?\});', html)
print(f"Var data matches: {len(visual_search_data)}")

# Find any valid image URLs and page links
img_matches = re.findall(r'"murl":"(https?://[^"]+)"', html)
print(f'"murl" count: {len(img_matches)}')
if img_matches:
    for u in img_matches[:5]:
        print("Murl:", u)

# Check for cbir URL redirection
print("Current URL:", r1.url)
