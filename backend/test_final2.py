import urllib.request
import json

print("=== 测试改进后的脚本生成 ===\n")

# 生成脚本
generate_url = 'http://127.0.0.1:8000/api/v1/ui/playwright/generate'
generate_data = json.dumps({
    'case': {
        'id': 'test_case',
        'name': '百度搜索',
        'url': 'https://www.baidu.com',
        'steps': [
            {'type': 'input', 'name': '搜索框', 'element': '搜索框', 'params': {'value': 'hello'}},
            {'type': 'click', 'name': '搜索', 'element': '搜索'},
            {'type': 'screenshot', 'name': '截图'}
        ]
    }
}).encode()

req = urllib.request.Request(generate_url, data=generate_data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    print("生成的脚本:")
    print("-" * 60)
    print(result.get('script', ''))
    print("-" * 60)
except Exception as e:
    print(f"生成失败: {e}")
    exit(1)

# 执行脚本
print("\n执行脚本...")
execute_url = 'http://127.0.0.1:8000/api/v1/ui/playwright/execute'
execute_data = json.dumps({
    'script': result.get('script', ''),
    'headless': True,
    'auto_execute': True
}).encode()

req2 = urllib.request.Request(execute_url, data=execute_data, headers={'Content-Type': 'application/json'})

try:
    resp2 = urllib.request.urlopen(req2, timeout=70)
    exec_result = json.loads(resp2.read().decode())
    r = exec_result.get('result', {})
    print(f"状态: {r.get('status')}")
    for step in r.get('steps', []):
        print(f"  {step.get('name')}: {step.get('status')} - {step.get('detail')}")
    print("\n日志:")
    for log in r.get('logs', [])[:20]:
        print(f"  {log}")
except Exception as e:
    print(f"执行失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")