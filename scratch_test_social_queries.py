import requests, json, urllib.parse, re
from html import unescape

def test_query(q):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    print(f'=== Testing query: {q} ===')
    url = f'https://www.bing.com/images/search?q={urllib.parse.quote(q)}&first=1'
    resp = requests.get(url, headers=headers, timeout=10)
    matches = re.findall(r'class="iusc"[^>]*m="([^"]+)"', resp.text)
    print(f'Matches found: {len(matches)}')
    for m in matches[:5]:
        data = json.loads(unescape(m))
        print(' - Title:', data.get('t'))
        print('   Page:', data.get('purl'))
        print('   Image:', data.get('murl'))

test_query('"Aditya Pratap Singh Tomar" linkedin')
test_query('Aditya Pratap Singh Tomar linkedin')
test_query('"Aditya Tomar" linkedin')
test_query('"Aditya Pratap Singh Tomar" instagram')
test_query('Aditya Pratap Singh Tomar github')
