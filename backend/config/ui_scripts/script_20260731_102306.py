#!/usr/bin/env python3
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
