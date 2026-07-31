import urllib.request
import json
import time

print("=== 测试 Playwright 改进功能 ===\n")

# 1. 测试脚本生成（包含 slow_mo 和操作间隔）
print("1. 测试脚本生成（验证 slow_mo 和操作间隔）")
url = 'http://127.0.0.1:8000/api/v1/ui/playwright/generate'
data = json.dumps({
    'case_id': 'test-case-1'  # 使用一个存在的用例ID
}).encode()

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    if result.get('success'):
        script = result.get('script', '')
        
        # 检查是否包含 slow_mo
        if 'slow_mo' in script:
            print("  ✓ 脚本包含 slow_mo 参数")
        else:
            print("  ✗ 脚本缺少 slow_mo 参数")
        
        # 检查是否包含 STEP_DELAY
        if 'STEP_DELAY' in script:
            print("  ✓ 脚本包含 STEP_DELAY 配置")
        else:
            print("  ✗ 脚本缺少 STEP_DELAY 配置")
        
        # 检查是否包含 wait_for_timeout
        if 'wait_for_timeout(STEP_DELAY)' in script:
            print("  ✓ 脚本包含操作间隔等待")
        else:
            print("  ✗ 脚本缺少操作间隔等待")
        
        # 检查是否包含 wait_for_captcha_input
        if 'wait_for_captcha_input' in script:
            print("  ✓ 脚本包含验证码等待函数")
        else:
            print("  ✗ 脚本缺少验证码等待函数")
        
        # 检查是否包含 SESSION_ID
        if 'SESSION_ID' in script:
            print("  ✓ 脚本包含验证码会话ID")
        else:
            print("  ✗ 脚本缺少验证码会话ID")
        
        # 检查是否包含视口设置
        if 'viewport' in script:
            print("  ✓ 脚本包含视口设置")
        else:
            print("  ✗ 脚本缺少视口设置")
        
        print("\n  脚本预览（前500字符）:")
        print(script[:500])
    else:
        print(f"  ✗ 生成失败: {result.get('detail')}")
except Exception as e:
    print(f"  ✗ 请求失败: {e}")

# 2. 测试验证码API
print("\n2. 测试验证码输入API")
test_session_id = "test-session-12345"

# 检查验证码状态
try:
    resp = urllib.request.urlopen(f'http://127.0.0.1:8000/api/v1/ui/playwright/captcha/status/{test_session_id}', timeout=5)
    result = json.loads(resp.read().decode())
    print(f"  ✓ 查询验证码状态: {result.get('status')}")
except Exception as e:
    print(f"  ✗ 查询失败: {e}")

# 提交验证码
try:
    data = json.dumps({
        'session_id': test_session_id,
        'captcha_code': 'test123'
    }).encode()
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/ui/playwright/captcha/input', data=data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=5)
    result = json.loads(resp.read().decode())
    print(f"  ✓ 提交验证码: {result.get('message')}")
    
    # 再次检查状态
    resp = urllib.request.urlopen(f'http://127.0.0.1:8000/api/v1/ui/playwright/captcha/status/{test_session_id}', timeout=5)
    result = json.loads(resp.read().decode())
    print(f"  ✓ 验证码状态更新: {result.get('status')}")
except Exception as e:
    print(f"  ✗ 提交失败: {e}")

# 3. 测试执行脚本（验证操作间隔）
print("\n3. 测试脚本执行（验证操作间隔）")
simple_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def run_test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, slow_mo=500)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()
            
            # 打开页面
            await page.goto("https://www.baidu.com", wait_until="domcontentloaded")
            print("Step 1: Opened page")
            await page.wait_for_timeout(800)
            
            # 搜索
            await page.get_by_role("textbox").fill("hello world")
            print("Step 2: Filled search")
            await page.wait_for_timeout(800)
            
            # 点击搜索按钮
            await page.get_by_role("button", name="百度一下").click()
            print("Step 3: Clicked search button")
            await page.wait_for_timeout(800)
            
            print("Step 4: Test completed")
            await browser.close()
            print("✓ All steps completed successfully")
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_test())
'''

try:
    data = json.dumps({
        'script': simple_script,
        'headless': True,
        'auto_execute': True
    }).encode()
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/ui/playwright/execute', data=data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=70)
    result = json.loads(resp.read().decode())
    r = result.get('result', {})
    
    print(f"  执行状态: {r.get('status')}")
    print("  步骤:")
    for step in r.get('steps', []):
        print(f"    {step.get('name')}: {step.get('status')}")
    print("  日志:")
    for log in r.get('logs', [])[:8]:
        print(f"    {log}")
    
    if r.get('status') == 'completed':
        print("  ✓ 脚本执行成功，操作间隔正常")
    else:
        print(f"  ✗ 执行状态: {r.get('status')}")
except Exception as e:
    print(f"  ✗ 执行失败: {e}")

print("\n=== 测试完成 ===")