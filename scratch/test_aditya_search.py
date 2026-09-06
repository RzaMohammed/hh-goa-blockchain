import requests, re, json, urllib.parse
from html import unescape
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def search_bing(query, max_res=5):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&first=1&qft=+filterui:face-face"
    r = requests.get(url, headers=headers, timeout=8)
    matches = re.findall(r'class="iusc"[^>]*m="([^"]+)"', r.text)
    results = []
    for m in matches[:max_res]:
        try:
            d = json.loads(unescape(m))
            results.append({
                'title': d.get('t'),
                'page': d.get('purl'),
                'img': d.get('murl')
            })
        except Exception:
            pass
    return results

# Test searching for Aditya Tomar on LinkedIn and Instagram
res_li = search_bing("site:linkedin.com/in Aditya Tomar portrait")
print(f"LinkedIn matches: {len(res_li)}")
for r in res_li[:3]:
    print("  Title:", r['title'])
    print("  Page:", r['page'])
    print("  Img:", r['img'])

res_ig = search_bing("site:instagram.com Aditya Tomar face")
print(f"Instagram matches: {len(res_ig)}")
for r in res_ig[:3]:
    print("  Title:", r['title'])
    print("  Page:", r['page'])
    print("  Img:", r['img'])
