import urllib.request
import json

print("=== 测试改进后的脚本生成和执行 ===\n")

# 步骤1: 生成脚本
print("步骤1: 生成Playwright脚本")
generate_url = 'http://127.0.0.1:8000/api/v1/ui/playwright/generate'
generate_data = json.dumps({
    'case': {
        'id': 'test_case_001',
        'name': '百度搜索测试',
        'url': 'https://www.baidu.com',
        'steps': [
            {'type': 'navigate', 'name': '打开页面', 'params': {'url': 'https://www.baidu.com'}},
            {'type': 'input', 'name': '搜索框', 'element': '搜索框', 'params': {'value': 'Playwright'}},
            {'type': 'click', 'name': '搜索按钮', 'element': '搜索按钮'},
            {'type': 'screenshot', 'name': '截图'}
        ]
    }
}).encode()

req1 = urllib.request.Request(generate_url, data=generate_data, headers={'Content-Type': 'application/json'})

try:
    resp1 = urllib.request.urlopen(req1, timeout=10)
    gen_result = json.loads(resp1.read().decode())
    print(f"  生成成功: {gen_result.get('success')}")
    generated_script = gen_result.get('script', '')
    print(f"\n生成的脚本内容:")
    print("-" * 60)
    print(generated_script)
    print("-" * 60)
except Exception as e:
    print(f"  生成失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 步骤2: 执行脚本
print("\n步骤2: 执行脚本")
execute_url = 'http://127.0.0.1:8000/api/v1/ui/playwright/execute'
execute_data = json.dumps({
    'script': generated_script,
    'headless': True,
    'auto_execute': True
}).encode()

req2 = urllib.request.Request(execute_url, data=execute_data, headers={'Content-Type': 'application/json'})

try:
    resp2 = urllib.request.urlopen(req2, timeout=70)
    exec_result = json.loads(resp2.read().decode())
    print(f"  执行成功: {exec_result.get('success')}")
    
    result = exec_result.get('result', {})
    print(f"  状态: {result.get('status')}")
    
    print("  执行步骤:")
    for step in result.get('steps', []):
        print(f"    - {step.get('name')}: {step.get('status')} ({step.get('detail')})")
    
    print("\n  执行日志:")
    for log in result.get('logs', []):
        print(f"    {log}")
    
    if result.get('status') == 'completed':
        print("\n✓ 测试通过！脚本执行成功！")
    elif result.get('status') == 'browser_missing':
        print("\n✗ 浏览器未安装")
    else:
        print(f"\n✗ 执行失败，状态: {result.get('status')}")
        
except urllib.error.HTTPError as e:
    print(f"  HTTP错误: {e.code}")
    body = e.read().decode()
    print(f"  错误详情: {body[:1000]}")
except Exception as e:
    print(f"  执行失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")