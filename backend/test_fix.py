import urllib.request
import json
import os

print("=== 测试修复后的功能 ===\n")

# 1. 测试脚本保存API
print("1. 测试脚本保存API")
test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def run_test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.baidu.com")
            print("Test completed!")
            await browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
'''

url = 'http://127.0.0.1:8000/api/v1/ui/playwright/save'
data = json.dumps({
    'script': test_script,
    'case_name': '测试用例'
}).encode()

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    if result.get('success'):
        print(f"  ✓ 脚本保存成功: {result.get('filename')}")
        print(f"  ✓ 文件路径: {result.get('filepath')}")
        
        # 检查路径是否正确（不包含 ..）
        filepath = result.get('filepath', '')
        if '..' not in filepath:
            print(f"  ✓ 路径正确（无相对路径）")
        else:
            print(f"  ✗ 路径包含相对路径: {filepath}")
        
        # 检查文件是否存在
        if os.path.exists(filepath):
            print(f"  ✓ 文件已创建")
        else:
            print(f"  ✗ 文件未创建")
    else:
        print(f"  ✗ 保存失败: {result.get('detail')}")
except Exception as e:
    print(f"  ✗ 请求失败: {e}")

# 2. 测试获取脚本列表
print("\n2. 测试获取脚本列表")
try:
    resp = urllib.request.urlopen('http://127.0.0.1:8000/api/v1/ui/playwright/scripts', timeout=10)
    result = json.loads(resp.read().decode())
    if result.get('success'):
        scripts = result.get('scripts', [])
        print(f"  ✓ 获取成功，共 {len(scripts)} 个脚本")
        for script in scripts[:3]:
            print(f"    - {script['filename']} ({script['size']} bytes)")
except Exception as e:
    print(f"  ✗ 请求失败: {e}")

# 3. 测试执行保存的脚本
print("\n3. 测试脚本执行（验证路径修复）")
execute_data = json.dumps({
    'script': test_script,
    'headless': True,
    'auto_execute': True
}).encode()

execute_req = urllib.request.Request('http://127.0.0.1:8000/api/v1/ui/playwright/execute', 
                                      data=execute_data, 
                                      headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(execute_req, timeout=60)
    result = json.loads(resp.read().decode())
    r = result.get('result', {})
    
    print(f"  执行状态: {r.get('status')}")
    
    # 检查日志中是否有WinError或SyntaxWarning
    logs = r.get('logs', [])
    has_error = False
    for log in logs:
        if 'WinError' in str(log) or 'SyntaxWarning' in str(log):
            print(f"  ✗ 仍有错误: {log}")
            has_error = True
    
    if not has_error:
        print(f"  ✓ 无路径错误或语法警告")
    
    if r.get('status') == 'completed':
        print(f"  ✓ 脚本执行成功")
    else:
        print(f"  执行日志:")
        for log in logs[:10]:
            print(f"    {log}")
except Exception as e:
    print(f"  ✗ 请求失败: {e}")

print("\n=== 测试完成 ===")