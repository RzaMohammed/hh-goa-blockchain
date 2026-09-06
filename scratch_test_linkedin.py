import requests, re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

urls = [
    "https://in.linkedin.com/in/aditya-pratap-singh-tomar-693444204",
    "https://in.linkedin.com/in/aditya-pratap-singh-tomar-b52228232",
    "https://www.linkedin.com/in/aditya-pratap-singh-b653271b3"
]

for u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=10)
        print(f"URL: {u} -> Status: {r.status_code}")
        og_img = re.search(r'<meta property="og:image" content="([^"]+)"', r.text) or re.search(r'<meta name="image" content="([^"]+)"', r.text)
        og_title = re.search(r'<meta property="og:title" content="([^"]+)"', r.text)
        if og_img:
            print("  og:image:", og_img.group(1))
        if og_title:
            print("  og:title:", og_title.group(1))
    except Exception as e:
        print(f"Error {u}: {e}")
