import urllib.request
import json
import urllib.error

url = 'http://127.0.0.1:8000/api/v1/ui/record/browser/start'
data = json.dumps({'url': 'https://www.baidu.com', 'headless': False}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read().decode())
    print('Success:', result.get('success'))
    print('Status:', result.get('status'))
    print('Session ID:', result.get('session_id'))
    print('Message:', result.get('message'))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
    body = e.read().decode()
    print('Error body:', body)
except Exception as e:
    print('Error:', str(e))
