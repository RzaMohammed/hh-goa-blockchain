import requests, io, re

with open('input/cropped_face_query.jpg', 'rb') as f:
    b = f.read()

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
})
r = s.get('https://www.bing.com/visualsearch', allow_redirects=True)
print("VisualSearch page status:", r.status_code, "url:", r.url)

# Search for upload endpoints in the html
endpoints = re.findall(r'https?://[^\s"\'<>]+/images/[^\s"\'<>]+', r.text)
print("Found endpoints:", set([e for e in endpoints if 'upload' in e.lower() or 'sbi' in e.lower() or 'vs' in e.lower()]))

# Let's also check Lens / Yandex / DuckDuckGo / Openverse / Wikipedia / Google
# Can we search DuckDuckGo images or Bing images with face filters?
