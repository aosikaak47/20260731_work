import urllib.request
import json

print("=== 测试脚本执行 ===\n")

# 直接执行一个简单的Playwright脚本
script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def run_test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto("https://www.baidu.com", wait_until="domcontentloaded")
            print("Page title:", await page.title())
            
            await browser.close()
            print("Test completed successfully")
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_test())
'''

url = 'http://127.0.0.1:8000/api/v1/ui/playwright/execute'
data = json.dumps({
    'script': script,
    'headless': True,
    'auto_execute': True
}).encode()

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=70)
    result = json.loads(resp.read().decode())
    r = result.get('result', {})
    print(f"状态: {r.get('status')}")
    print("步骤:")
    for step in r.get('steps', []):
        print(f"  {step.get('name')}: {step.get('status')} - {step.get('detail')}")
    print("\n日志:")
    for log in r.get('logs', [])[:15]:
        print(f"  {log}")
    
    if r.get('status') == 'completed':
        print("\n✓ 测试通过！")
    else:
        print(f"\n✗ 执行状态: {r.get('status')}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")