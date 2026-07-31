#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: http://192.168.100.167/hxkr/#/config/appCenter
# 生成时间: 2026-07-31 11:39:18
# 操作数量: 11

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
        await page.goto("http://192.168.100.167/hxkr/#/config/appCenter")
        await page.wait_for_load_state("networkidle")

        # 步骤1: 页面导航
        await page.goto("http://192.168.100.167/hxkr/#/passport/login")
        await page.wait_for_load_state("networkidle")

        # 步骤2: 点击元素
        await page.locator("#form_item_username").click()

        # 步骤3: 输入文本
        await page.locator("#form_item_username").fill("ad")

        # 步骤4: 输入文本
        await page.locator("#form_item_username").fill("admin")

        # 步骤5: 点击元素
        await page.locator("#form_item_password").click()

        # 步骤6: 输入文本
        await page.locator("#form_item_password").fill("JS")

        # 步骤7: 输入文本
        await page.locator("#form_item_password").fill("JS_")

        # 步骤8: 输入文本
        await page.locator("#form_item_password").fill("JS_M258369")

        # 步骤9: 点击元素
        await page.locator("div > div > div > div > span").click()

        # 步骤10: 点击元素
        await page.locator("span > span:nth-of-type(2) > span > svg > path:nth-of-type(1)").click()

        # 步骤11: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div > button > span").click()

        # 截图保存
        await page.screenshot(path="test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())