import requests

for term in ['adityatomar8123', 'Aditya Pratap Singh Tomar', 'Aditya Tomar']:
    res = requests.get(f'https://api.github.com/search/users?q={term}', headers={'User-Agent': 'CyberSightBiometrics/1.0'})
    print(f'Term: {term} -> Status: {res.status_code}')
    if res.status_code == 200:
        items = res.json().get('items', [])
        print(f'  Found {len(items)} users:')
        for u in items[:3]:
            login = u.get("login")
            html_url = u.get("html_url")
            avatar_url = u.get("avatar_url")
            print(f'   - @{login}: {html_url} | Avatar: {avatar_url}')
