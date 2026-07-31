# Playwright 自动化测试脚本 (Python)
# 用例名称: 用例搜索功能
# 生成时间: 2026-07-31 10:56:49

import asyncio
from playwright.async_api import async_playwright

async def run_test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # 打开目标页面
            await page.goto("http://localhost:5173/case-list", wait_until="domcontentloaded")

            # 打开用例列表
            await page.goto("http://localhost:5173/case-list", wait_until="domcontentloaded")

            # 输入搜索关键字
            input_value = "登录"
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

            # 点击搜索按钮
            raise Exception("No element specified for click")

            await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_105656/test_result.png")
            await browser.close()
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_test())