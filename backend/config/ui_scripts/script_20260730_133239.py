# Playwright 自动化测试脚本 (Python)
import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://example.com')
        print('Title:', await page.title())
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
