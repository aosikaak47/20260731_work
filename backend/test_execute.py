import urllib.request
import json

# 测试脚本执行
script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.baidu.com")
        print("Page title:", await page.title())
        
        await browser.close()
        print("Test completed successfully")

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
    print('Success:', result.get('success'))
    
    execution_result = result.get('result', {})
    print('Status:', execution_result.get('status'))
    print('Steps:')
    for step in execution_result.get('steps', []):
        print(f"  - {step.get('name')}: {step.get('status')} ({step.get('detail')})")
    print('Logs:')
    for log in execution_result.get('logs', []):
        print(f"  {log}")
    
except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    body = e.read().decode()
    print(f'Error body: {body[:2000]}')
except Exception as e:
    print(f'Error: {str(e)}')
    import traceback
    traceback.print_exc()