# Playwright 自动化测试脚本 (Python)
# 用例名称: 登录功能测试
# 生成时间: 2026-07-30 12:19:59

import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开目标页面
        await page.goto("http://localhost:5173/login")

        # 打开登录页
        await page.goto("http://localhost:5173/login")

        # 输入用户名
        await page.locator("//input[@name='username']").fill("admin")

        # 输入密码
        await page.locator("//input[@name='password']").fill("123456")

        # 点击登录
        await page.locator("button.login-btn").click()

        # 验证登录成功
        await expect(page.get_by_text("首页工作台")).to_be_visible()

        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260730_122001/test_result.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())