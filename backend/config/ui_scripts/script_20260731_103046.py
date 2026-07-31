# Playwright 自动化测试脚本 (Python)
# 用例名称: 百度搜索测试
# 生成时间: 2026-07-31 10:30:46

import asyncio
from playwright.async_api import async_playwright

async def run_test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # 打开目标页面
            await page.goto("https://www.baidu.com", wait_until="domcontentloaded")

            # 打开页面
            await page.goto("https://www.baidu.com", wait_until="domcontentloaded")

            # 搜索框
            try:
                await page.locator("input.search-input").wait_for(state="visible", timeout=10000)
                await page.locator("input.search-input").fill("Playwright")
            except Exception:
                await page.locator("input.search-input").fill("Playwright", force=True)

            # 搜索按钮
            try:
                await page.get_by_text("搜索按钮").wait_for(state="visible", timeout=10000)
                await page.get_by_text("搜索按钮").click()
            except Exception:
                await page.get_by_text("搜索按钮").click(force=True)

            # 截图
            await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_103046/screenshot_4.png")

            await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_103046/test_result.png")
            await browser.close()
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_test())