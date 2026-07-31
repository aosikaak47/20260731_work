# Playwright 自动化测试脚本 (Python)
# 用例名称: 百度搜索
# 生成时间: 2026-07-31 10:44:26

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

            # 搜索框
            input_value = "hello"
            input_done = False
            for loc_expr in [
                lambda: page.locator("input.search-input"),
                lambda: page.get_by_role("textbox", name="搜索框"),
                lambda: page.get_by_placeholder("搜索框"),
                lambda: page.locator("input").first
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill(input_value)
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("input").first.fill(input_value, force=True)

            # 搜索
            click_done = False
            for loc_expr in [
                lambda: page.get_by_text("搜索"),
                lambda: page.get_by_role("button", name="搜索"),
                lambda: page.get_by_role("link", name="搜索"),
                lambda: page.locator("button").first
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.click()
                    click_done = True
                    break
                except Exception:
                    continue
            if not click_done:
                raise Exception("Failed to click: 搜索")

            # 截图
            await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_104426/screenshot_3.png")

            await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_104426/test_result.png")
            await browser.close()
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_test())