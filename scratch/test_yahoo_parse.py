import requests, re, urllib.parse

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
r = requests.get('https://images.search.yahoo.com/search/images?p=person+face+portrait', headers=headers, timeout=8)

# Find around imgurl
for m in re.finditer(r'imgurl=([^&"\'<>\s]+)', r.text):
    start = max(0, m.start() - 100)
    end = min(len(r.text), m.end() + 200)
    snippet = r.text[start:end]
    print("Snippet:", snippet)
    break
