import urllib.request
import json
import os
import time

# 测试新的录制API
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
    
    session_id = result.get('session_id')
    
    # 等待几秒
    time.sleep(3)
    
    # 检查record_file
    record_file = result.get('record_file')
    if record_file and os.path.exists(record_file):
        with open(record_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print('\nRecord file status:', data.get('status'))
        print('Actions count:', len(data.get('actions', [])))
        
        # 如果状态是starting，说明浏览器进程可能没有运行
        if data.get('status') == 'starting':
            print('WARNING: Browser may not have started properly!')
    else:
        print('Record file not found')
    
    # 查找最新生成的recorder脚本，检查是否有语法错误
    import glob
    scripts_dir = 'e:/trae_work/autoProject/backend/config/ui_scripts'
    py_files = sorted(glob.glob(os.path.join(scripts_dir, f'recorder_{session_id}*.py')))
    if py_files:
        latest = py_files[-1]
        print(f'\nGenerated recorder script: {os.path.basename(latest)}')
        
        # 检查是否有双花括号
        with open(latest, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '{{' in content:
            print('ERROR: Double braces found in generated script!')
        else:
            print('OK: No double braces in generated script')
        
        if '}}' in content:
            print('ERROR: Double braces found in generated script!')
        else:
            print('OK: No double braces in generated script')
        
        # 检查关键行
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'dict(' in line or ('"actions"' in line and 'status' in line):
                print(f'  Line {i+1}: {line.strip()}')
        
        # 语法检查
        import py_compile
        try:
            py_compile.compile(latest, doraise=True)
            print('Syntax check: PASSED!')
        except py_compile.PyCompileError as e:
            print(f'Syntax check: FAILED - {e}')
    
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
    body = e.read().decode()
    print('Error body:', body)
except Exception as e:
    print('Error:', str(e))
    import traceback
    traceback.print_exc()