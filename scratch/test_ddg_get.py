import requests, re, urllib.parse, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

def search_ddg(query):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    r = requests.get(url, headers=headers, timeout=8)
    matches = re.findall(r'<a class="result__url" href="([^"]+)">([^<]+)</a>', r.text)
    results = []
    for href, title in matches:
        m = re.search(r'uddg=([^&]+)', href)
        if m:
            actual_url = urllib.parse.unquote(m.group(1))
            results.append((actual_url, title.strip()))
    return results

for url, title in search_ddg("Aditya Pratap Singh Tomar linkedin")[:5]:
    print("URL:", url, "Title:", title)
