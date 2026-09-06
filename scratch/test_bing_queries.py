import requests, re, json, urllib.parse
from html import unescape

def search_bing_images(query, max_results=20):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    b_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&first=1&qft=+filterui:face-face"
    resp = requests.get(b_url, headers=headers, timeout=10)
    print("Bing status:", resp.status_code)
    
    matches = re.findall(r'class="iusc"[^>]*m="([^"]+)"', resp.text)
    print(f"Found {len(matches)} matches")
    results = []
    for raw in matches[:max_results]:
        try:
            item = json.loads(unescape(raw))
            img_url = item.get('murl')
            page_url = item.get('purl')
            title = item.get('t') or item.get('desc')
            results.append({'title': title, 'image_url': img_url, 'source_url': page_url})
        except Exception as e:
            pass
    return results

res = search_bing_images("site:instagram.com person portrait face", 5)
for r in res:
    print(r)
