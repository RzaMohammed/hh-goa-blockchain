import requests, re, urllib.parse, sys
from html import unescape
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Test Yahoo Web Search
try:
    y_url = "https://search.yahoo.com/search?p=Aditya+Pratap+Singh+Tomar+linkedin"
    r = requests.get(y_url, headers=headers, timeout=6)
    print("Yahoo status:", r.status_code)
    # Find links
    links = re.findall(r'href="(https?://[^"]*linkedin\.com/in/[^"]*)"', r.text)
    print("Yahoo LinkedIn links found:", len(links))
    for l in links[:5]:
        print("  ->", l)
except Exception as e:
    print("Yahoo error:", e)

# Test DuckDuckGo HTML
try:
    ddg_url = "https://html.duckduckgo.com/html/?q=Aditya+Pratap+Singh+Tomar+linkedin"
    r = requests.get(ddg_url, headers=headers, timeout=6)
    print("DDG status:", r.status_code)
    links = re.findall(r'class="result__url"[^>]*href="([^"]+)"', r.text)
    print("DDG links found:", len(links))
    for l in links[:5]:
        print("  ->", l)
except Exception as e:
    print("DDG error:", e)
