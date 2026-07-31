#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: https://www.baidu.com
# 生成时间: 2026-07-31 09:01:10
# 操作数量: 2

import asyncio
from playwright.async_api import async_playwright


async def test_录制场景():
    """
    录制场景
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开目标页面
        await page.goto("https://www.baidu.com")
        await page.wait_for_load_state("networkidle")

        # 步骤1: 点击元素
        # 目标: search
        await page.locator("#kw").click()

        # 步骤2: 输入文本
        await page.locator("#kw").fill("test")

        # 截图保存
        await page.screenshot(path="test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())