import requests, re, urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def test_ddg_html(query):
    print(f"=== DDG HTML: {query} ===")
    url = "https://html.duckduckgo.com/html/"
    try:
        resp = requests.post(url, data={"q": query}, headers=headers, timeout=10)
        print("Status:", resp.status_code)
        # Regex search for links
        urls = re.findall(r'<a class="result__url"[^>]*href="([^"]+)"', resp.text)
        titles = re.findall(r'<a class="result__snippet"[^>]*>([^<]+)</a>', resp.text)
        print(f"Found {len(urls)} results:")
        for u in urls[:5]:
            print(" - URL:", u)
    except Exception as e:
        print("DDG Error:", e)

def test_yahoo_images(query):
    print(f"=== Yahoo Images: {query} ===")
    url = f"https://images.search.yahoo.com/search/images?p={urllib.parse.quote(query)}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print("Status:", resp.status_code)
        img_urls = re.findall(r'img data-src="([^"]+)"', resp.text) or re.findall(r'src="(https://tse[^"]+)"', resp.text)
        print(f"Found {len(img_urls)} images:")
        for u in img_urls[:3]:
            print(" -", u[:80])
    except Exception as e:
        print("Yahoo Error:", e)

test_ddg_html("site:instagram.com Aditya Pratap Singh Tomar")
test_ddg_html("site:linkedin.com/in Aditya Pratap Singh Tomar")
test_yahoo_images("Aditya Pratap Singh Tomar")
