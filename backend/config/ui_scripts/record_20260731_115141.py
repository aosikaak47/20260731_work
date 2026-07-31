#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 百度搜索测试
# 目标URL: https://www.baidu.com
# 生成时间: 2026-07-31 11:51:41
# 操作数量: 3

import asyncio
from playwright.async_api import async_playwright

# 配置
SLOW_MO = 500  # 操作间隔(ms)，模拟人类操作速度
STEP_DELAY = 800  # 步骤间延迟(ms)
HEADLESS = False  # 是否无头模式


async def test_百度搜索测试():
    """
    百度搜索测试
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            # 打开目标页面
            await page.goto("https://www.baidu.com", wait_until="domcontentloaded")
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤1: 页面导航
            await page.goto("https://www.baidu.com", wait_until="domcontentloaded")
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤2: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("#kw"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("Playwright自动化测试")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("#kw").fill("Playwright自动化测试", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤3: 点击元素
            # 目标: 百度一下
            click_done = False
            for loc_expr in [
                lambda: page.locator("#su"),
                lambda: page.get_by_text("百度一下"),
                lambda: page.get_by_role("button"),
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
                await page.locator("#su").click(force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 截图保存
            await page.screenshot(path="test_result.png")
            await browser.close()
            print("✓ 测试执行完成")
    except Exception as e:
        print(f"✗ 测试执行失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_百度搜索测试())