import urllib.request, json

req = urllib.request.Request(
    'http://localhost:8080/api/pipeline/run',
    data=json.dumps({'max_candidates': 8, 'platform': 'all'}).encode(),
    headers={'Content-Type': 'application/json'}
)
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())
print('Pipeline Success:', data.get('success'))
print('Verdict:', data.get('verdict'))
print('Best candidate label:', data.get('best_candidate', {}).get('label'))
print('Best score:', data.get('best_score'))
print('Candidates count:', len(data.get('candidates', [])))
for c in data.get('candidates', []):
    plat = c.get('platform')
    src = c.get('source_name')
    label = c.get('label')
    score = c.get('score')
    link = c.get('link', '')[:50]
    print(f" - [{plat}] {src}: {label} ({score}%) -> {link}")
