import urllib.request
import json
import os
import time

print("=== 测试录制浏览器启动 ===")

# 测试新的录制API
url = 'http://127.0.0.1:8000/api/v1/ui/record/browser/start'
data = json.dumps({'url': 'https://www.baidu.com', 'headless': False}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=20)
    result = json.loads(resp.read().decode())
    print('API响应 - Success:', result.get('success'))
    print('API响应 - Status:', result.get('status'))
    print('API响应 - Session ID:', result.get('session_id'))
    print('API响应 - Message:', result.get('message'))
    
    if result.get('success'):
        session_id = result.get('session_id')
        record_file = result.get('record_file')
        log_file = result.get('log_file')
        
        print(f'\n等待5秒让浏览器完全启动...')
        time.sleep(5)
        
        # 检查record_file状态
        if record_file and os.path.exists(record_file):
            with open(record_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f'Record file status: {data.get("status")}')
            print(f'Actions count: {len(data.get("actions", []))}')
        else:
            print('Record file not found')
        
        # 检查日志文件
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            print(f'\nLog file content ({len(log_content)} chars):')
            print(log_content[:1000] if log_content else '(empty)')
        else:
            print('Log file not found')
        
        # 查询会话状态
        try:
            status_url = f'http://127.0.0.1:8000/api/v1/ui/record/{session_id}'
            resp2 = urllib.request.urlopen(status_url, timeout=10)
            status_result = json.loads(resp2.read().decode())
            print(f'\nSession status: {status_result.get("session", {}).get("status")}')
            print(f'Actions: {len(status_result.get("session", {}).get("actions", []))}')
        except Exception as e:
            print(f'Error checking status: {e}')
        
        print('\n=== 测试完成 ===')
        print('请检查是否有浏览器窗口弹出！')
    else:
        print('API返回失败')
        
except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    body = e.read().decode()
    print(f'Error body: {body}')
except Exception as e:
    print(f'Error: {str(e)}')
    import traceback
    traceback.print_exc()