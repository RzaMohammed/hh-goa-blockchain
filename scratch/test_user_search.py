import requests, re, json, urllib.parse, sys
from html import unescape

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

queries = [
    '"Aditya Pratap Singh Tomar"',
    'site:linkedin.com/in "Aditya Pratap Singh Tomar"',
    '"Aditya Pratap Singh Tomar" face OR portrait',
    '"Aditya Tomar" face profile headshot',
]

for q in queries:
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(q)}&first=1&qft=+filterui:face-face"
    r = requests.get(url, headers=headers, timeout=6)
    matches = re.findall(r'class="iusc"[^>]*m="([^"]+)"', r.text)
    print(f"Query '{q}': {len(matches)} matches")
    for m in matches[:3]:
        d = json.loads(unescape(m))
        print("  Title:", d.get('t'))
        print("  Page:", d.get('purl'))
        print("  Img:", d.get('murl'))
