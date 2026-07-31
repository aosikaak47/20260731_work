#!/usr/bin/env python3
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
