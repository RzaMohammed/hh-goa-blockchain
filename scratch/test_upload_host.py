import requests

# Test uploading to tmpfiles.org or catbox or 0x0.st
try:
    with open('input/custom_upload.jpg', 'rb') as f:
        r = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f}, timeout=10)
    print("tmpfiles response:", r.status_code, r.text)
    if r.status_code == 200:
        data = r.json()
        url = data.get('data', {}).get('url')
        # tmpfiles direct url adds /dl/
        direct_url = url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
        print("Direct URL:", direct_url)
except Exception as e:
    print("Upload error:", e)
