import requests, re, urllib.parse, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

def search_ddg_profiles(query):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    r = requests.post(url, data={'q': query}, headers=headers, timeout=8)
    # Extract decoded destination URLs
    raw_links = re.findall(r'href="[^"]*uddg=([^&"]+)', r.text)
    decoded = [urllib.parse.unquote(l) for l in raw_links]
    return decoded

print("Instagram search:")
for l in search_ddg_profiles("site:instagram.com Aditya Pratap Singh Tomar")[:3]:
    print("  ->", l)

print("GitHub search:")
for l in search_ddg_profiles("site:github.com Aditya Pratap Singh Tomar")[:3]:
    print("  ->", l)

print("LinkedIn search:")
for l in search_ddg_profiles("site:linkedin.com/in Aditya Pratap Singh Tomar")[:3]:
    print("  ->", l)
