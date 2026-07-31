#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: http://192.168.100.167/hxkr/#/config/appCenter
# 生成时间: 2026-07-31 11:41:30
# 操作数量: 7

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

        # 步骤3: 点击元素
        await page.locator("#form_item_username").click()

        # 步骤4: 点击元素
        await page.locator("#form_item_username").click()

        # 步骤5: 点击元素
        await page.locator("#form_item_password").click()

        # 步骤6: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤7: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div > div > button").click()

        # 截图保存
        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_114134/test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())