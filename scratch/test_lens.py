import requests, io, re

with open('input/cropped_face_query.jpg', 'rb') as f:
    b = f.read()

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
})

# Test Google Lens upload
try:
    r = s.post('https://lens.google.com/v3/upload', files={'encoded_image': ('face.jpg', io.BytesIO(b), 'image/jpeg')}, allow_redirects=True, timeout=10)
    print("Google Lens v3 status:", r.status_code, "url:", r.url)
    print("Content length:", len(r.text))
    # Look for redirect or visual matches
    matches = re.findall(r'https?://[^"\'<>\s]+\.(?:jpg|jpeg|png|webp)', r.text)
    print("Image URLs found:", len(matches))
except Exception as e:
    print("Lens error:", e)

# Test Yandex
try:
    r_y = s.post('https://yandex.com/images-apphost/image-download?cname=cropper', files={'upfile': ('face.jpg', io.BytesIO(b), 'image/jpeg')}, timeout=10)
    print("Yandex status:", r_y.status_code, "text:", r_y.text[:200])
except Exception as e:
    print("Yandex error:", e)
