import requests, re, urllib.parse, json

img_url = "https://tmpfiles.org/dl/wZwnklOdTDRo/custom_upload.jpg"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# 1. Bing by URL
try:
    bing_url = f"https://www.bing.com/images/search?q=imgurl:{urllib.parse.quote(img_url)}&view=detailv2&iss=sbi"
    r = requests.get(bing_url, headers=headers, timeout=10)
    print("Bing by URL status:", r.status_code, "len:", len(r.text))
    # Check for visual matches or pagesIncludingImage
    m_matches = re.findall(r'class="iusc"[^>]*m="([^"]+)"', r.text)
    print("Bing m_matches:", len(m_matches))
    pages = re.findall(r'"pagesIncludingImage":\s*\[([^\]]+)\]', r.text)
    print("Bing pagesIncludingImage:", len(pages))
    if m_matches:
        from html import unescape
        for m in m_matches[:3]:
            d = json.loads(unescape(m))
            print("  Bing visual item:", d.get('t'), d.get('purl'), d.get('murl'))
except Exception as e:
    print("Bing error:", e)

# 2. Yandex by URL
try:
    y_url = f"https://yandex.com/images/search?rpt=imageview&url={urllib.parse.quote(img_url)}"
    r_y = requests.get(y_url, headers=headers, timeout=10)
    print("Yandex by URL status:", r_y.status_code, "len:", len(r_y.text))
    # Look for previews or tags
    y_matches = re.findall(r'"preview":\[\{"url":"(https?://[^"]+)"', r_y.text)
    print("Yandex preview matches:", len(y_matches))
    y_tags = re.findall(r'"tags":\[(.*?)\]', r_y.text)
    print("Yandex tags:", y_tags[:2])
except Exception as e:
    print("Yandex error:", e)
