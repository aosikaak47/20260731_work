# Playwright 自动化测试脚本 (Python)
# 用例名称: 百度搜索测试
# 生成时间: 2026-07-31 10:25:57

import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开目标页面
        await page.goto("https://www.baidu.com")

        # 打开页面
        await page.goto("https://www.baidu.com")

        # 输入搜索词
        await page.locator("input.search-input").fill("Playwright")

        # 点击搜索按钮
        await page.get_by_text("搜索按钮").click()

        # 截图
        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_102557/screenshot_4.png")

        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_102557/test_result.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())