import urllib.parse, re

PLATFORM_MAP = {
    "instagram.com": ("instagram", "Instagram"),
    "cdninstagram.com": ("instagram", "Instagram CDN"),
    "linkedin.com": ("linkedin", "LinkedIn"),
    "licdn.com": ("linkedin", "LinkedIn CDN"),
    "github.com": ("github", "GitHub"),
    "githubusercontent.com": ("github", "GitHub User Content"),
    "twitter.com": ("twitter", "Twitter / X"),
    "x.com": ("twitter", "Twitter / X"),
    "twimg.com": ("twitter", "Twitter / X CDN"),
    "t.co": ("twitter", "Twitter / X"),
    "facebook.com": ("facebook", "Facebook"),
    "fb.com": ("facebook", "Facebook"),
    "fbcdn.net": ("facebook", "Facebook CDN"),
    "reddit.com": ("reddit", "Reddit"),
    "redd.it": ("reddit", "Reddit"),
    "youtube.com": ("youtube", "YouTube"),
    "youtu.be": ("youtube", "YouTube"),
    "pinterest.com": ("pinterest", "Pinterest"),
    "pinimg.com": ("pinterest", "Pinterest CDN"),
    "tiktok.com": ("tiktok", "TikTok"),
    "wikipedia.org": ("wikipedia", "Wikipedia"),
    "wikimedia.org": ("wikipedia", "Wikimedia Commons"),
    "flickr.com": ("flickr", "Flickr"),
    "staticflickr.com": ("flickr", "Flickr CDN"),
    "unsplash.com": ("unsplash", "Unsplash"),
    "pexels.com": ("pexels", "Pexels"),
    "medium.com": ("medium", "Medium"),
    "quora.com": ("quora", "Quora"),
}

def resolve_source_info(url: str, img_url: str = "") -> dict:
    target_url = url or img_url or ""
    try:
        parsed = urllib.parse.urlparse(target_url)
        hostname = (parsed.hostname or "").lower()
    except Exception:
        hostname = ""

    # Strip leading www., m., etc.
    clean_host = re.sub(r'^(?:www\d*|m|mobile|l|i|preview)\.', '', hostname)

    # Check known platforms
    for domain, (slug, name) in PLATFORM_MAP.items():
        if clean_host == domain or clean_host.endswith("." + domain):
            return {
                "platform": slug,
                "source_name": name,
                "domain": clean_host
            }

    # If not in map, derive clean brand name
    if clean_host:
        parts = clean_host.split(".")
        if len(parts) >= 2:
            brand = parts[-2]
        else:
            brand = parts[0]
        brand_clean = re.sub(r'[-_]', ' ', brand).title()
        return {
            "platform": "web",
            "source_name": brand_clean,
            "domain": clean_host
        }

    return {
        "platform": "web",
        "source_name": "Web Source",
        "domain": "web"
    }

# Test samples
test_urls = [
    "https://www.instagram.com/p/C_abc123/",
    "https://i.pinimg.com/originals/2a/e7/7f/photo.jpg",
    "https://www.linkedin.com/in/johndoe",
    "https://github.com/torvalds",
    "https://twitter.com/elonmusk/status/123",
    "https://upload.wikimedia.org/wikipedia/commons/e/ed/Portrait.jpg",
    "https://rubgallery.com/portfolio/camillo-sitte/",
    "https://austria-forum.org/af/Wissenssammlungen/",
    "https://teorizandoaarquitetura.blogspot.com/2012/04/aula-09-",
    "https://alchetron.com/Camillo-Sitte",
    "https://www.lonelyplanet.com/articles/hiking",
]

for u in test_urls:
    res = resolve_source_info(u)
    print(f"{u[:45]:<48} -> platform={res['platform']:<12} name={res['source_name']}")
