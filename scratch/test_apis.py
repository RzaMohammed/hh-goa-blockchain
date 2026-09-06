import requests, re, json, urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# 1. Test Yahoo Image Search
try:
    y_url = "https://images.search.yahoo.com/search/images?p=person+face+portrait+headshot"
    r = requests.get(y_url, headers=headers, timeout=8)
    print("Yahoo status:", r.status_code)
    # Yahoo images often have <li class="ld"> or json data
    img_urls = re.findall(r'imgurl=([^&"\'<>\s]+)', r.text)
    print("Yahoo imgurl count:", len(img_urls))
    if not img_urls:
        # Check for data-url or src
        matches = re.findall(r'data-url="([^"]+)"', r.text)
        print("Yahoo data-url count:", len(matches))
except Exception as e:
    print("Yahoo error:", e)

# 2. Test Wikimedia Commons API
try:
    wm_url = "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=face%20portrait%20person&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&format=json&gsrlimit=10"
    r = requests.get(wm_url, headers={'User-Agent': 'CyberSightBiometric/1.0 (contact: admin@localhost)'}, timeout=8)
    print("Wikimedia status:", r.status_code)
    if r.status_code == 200:
        pages = r.json().get('query', {}).get('pages', {})
        print("Wikimedia images found:", len(pages))
        for k, v in list(pages.items())[:3]:
            info = v.get('imageinfo', [{}])[0]
            print("  Title:", v.get('title'))
            print("  URL:", info.get('url'))
            print("  Desc:", info.get('descriptionurl'))
except Exception as e:
    print("Wikimedia error:", e)

# 3. Test Openverse API
try:
    ov_url = "https://api.openverse.org/v1/images/?q=person%20face%20portrait&page_size=10"
    r = requests.get(ov_url, headers={'User-Agent': 'CyberSightBiometric/1.0'}, timeout=8)
    print("Openverse status:", r.status_code)
    if r.status_code == 200:
        results = r.json().get('results', [])
        print("Openverse images found:", len(results))
        for item in results[:3]:
            print("  Title:", item.get('title'))
            print("  URL:", item.get('url'))
            print("  Source:", item.get('foreign_landing_url'))
except Exception as e:
    print("Openverse error:", e)
