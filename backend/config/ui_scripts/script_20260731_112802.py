#!/usr/bin/env python3
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
