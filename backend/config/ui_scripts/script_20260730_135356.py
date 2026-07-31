# Playwright 自动化测试脚本 (Python)
# 用例名称: 测试用例1
# 生成时间: 2026-07-30 13:53:52

import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开目标页面
        await page.goto("https://example.com")

        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260730_135356/test_result.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())