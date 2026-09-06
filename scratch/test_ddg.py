import requests, re, json, urllib.parse

def search_duckduckgo_images(query, max_results=20):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }
    s = requests.Session()
    # Step 1: get vqd token
    res = s.get(f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&t=h_&iax=images&ia=images", headers=headers)
    vqd_match = re.search(r'vqd=([0-9-]+)', res.text) or re.search(r'vqd="([^"]+)"', res.text)
    if not vqd_match:
        print("No vqd found")
        return []
    vqd = vqd_match.group(1)
    print("Found vqd:", vqd)

    # Step 2: request images
    params = {
        'l': 'us-en',
        'o': 'json',
        'q': query,
        'vqd': vqd,
        'f': ',,,',
        'p': '1'
    }
    img_res = s.get("https://duckduckgo.com/i.js", headers=headers, params=params)
    data = img_res.json()
    results = data.get('results', [])
    print(f"DDG returned {len(results)} image results")
    for r in results[:5]:
        print("Title:", r.get('title'))
        print("Image:", r.get('image'))
        print("URL:", r.get('url'))
        print("---")
    return results

search_duckduckgo_images("site:instagram.com person portrait face")
