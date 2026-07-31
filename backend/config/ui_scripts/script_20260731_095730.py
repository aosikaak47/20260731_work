#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: http://192.168.100.50:54815/#/interFaceManagement
# 生成时间: 2026-07-31 09:57:21
# 操作数量: 18

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
        await page.goto("http://192.168.100.50:54815/#/interFaceManagement")
        await page.wait_for_load_state("networkidle")

        # 步骤1: 页面导航
        await page.goto("http://192.168.100.50:54815/#/indexTopLevel")
        await page.wait_for_load_state("networkidle")

        # 步骤2: 点击元素
        await page.locator("input[name=\"username\"]").click()

        # 步骤3: 输入文本
        await page.locator("input[name=\"username\"]").fill("aad")

        # 步骤4: 输入文本
        await page.locator("input[name=\"username\"]").fill("aa")

        # 步骤5: 输入文本
        await page.locator("input[name=\"username\"]").fill("a")

        # 步骤6: 输入文本
        await page.locator("input[name=\"username\"]").fill("admin")

        # 步骤7: 点击元素
        await page.locator("input[name=\"password\"]").click()

        # 步骤8: 点击元素
        await page.locator("input[name=\"username\"]").click()

        # 步骤9: 点击元素
        await page.locator("input[name=\"password\"]").click()

        # 步骤10: 输入文本
        await page.locator("input[name=\"password\"]").fill("JS")

        # 步骤11: 输入文本
        await page.locator("input[name=\"password\"]").fill("JS_")

        # 步骤12: 输入文本
        await page.locator("input[name=\"password\"]").fill("JS_m258369")

        # 步骤13: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div:nth-of-type(2) > div > div").click()

        # 步骤14: 点击元素
        await page.locator("div > div > span:nth-of-type(2) > span > i").click()

        # 步骤15: 点击元素
        await page.locator("input[name=\"password\"]").click()

        # 步骤16: 输入文本
        await page.locator("input[name=\"password\"]").fill("JS_M258369")

        # 步骤17: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div:nth-of-type(2) > div > div").click()

        # 步骤18: 页面导航
        await page.goto("http://192.168.100.50:54815/#/index")
        await page.wait_for_load_state("networkidle")

        # 截图保存
        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_095730/test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())