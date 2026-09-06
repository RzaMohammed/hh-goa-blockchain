import requests, json, re

def test_ddg_images(query):
    print(f'=== Testing DDG: {query} ===')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    
    # 1. Get vqd token
    res = requests.get(f'https://duckduckgo.com/?q={query}', headers=headers, timeout=10)
    vqd_match = re.search(r'vqd=([0-9-]+)', res.text) or re.search(r'vqd="([^"]+)"', res.text)
    if not vqd_match:
        print('Could not extract VQD')
        return
    vqd = vqd_match.group(1)
    print('VQD:', vqd)
    
    # 2. Query images endpoint
    img_url = f'https://duckduckgo.com/i.js?l=us-en&o=json&q={query}&vqd={vqd}&f=,,,&p=1'
    resp = requests.get(img_url, headers=headers, timeout=10)
    print('Img search status:', resp.status_code)
    try:
        data = resp.json()
        results = data.get('results', [])
        print(f'Found {len(results)} images:')
        for r in results[:5]:
            print(' - Title:', r.get('title'))
            print('   Source:', r.get('url'))
            print('   Image:', r.get('image'))
    except Exception as e:
        print('Parse error:', e)

test_ddg_images('Aditya Pratap Singh Tomar')
test_ddg_images('Aditya Tomar LinkedIn')
test_ddg_images('Aditya Tomar Instagram')
test_ddg_images('adityatomar8123')
