#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: http://192.168.100.167/hxkr/#/config/appCenter
# 生成时间: 2026-07-31 11:33:51
# 操作数量: 26

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
        await page.locator("#form_item_username").fill("admin")

        # 步骤4: 输入文本
        await page.locator("#form_item_username").fill("admin")

        # 步骤5: 点击元素
        await page.locator("#form_item_password").click()

        # 步骤6: 点击元素
        await page.locator("#form_item_password").click()

        # 步骤7: 输入文本
        await page.locator("#form_item_password").fill("JS")

        # 步骤8: 输入文本
        await page.locator("#form_item_password").fill("JS_")

        # 步骤9: 输入文本
        await page.locator("#form_item_password").fill("JS_M")

        # 步骤10: 输入文本
        await page.locator("#form_item_password").fill("JS_M258369")

        # 步骤11: 点击元素
        await page.locator("div > div > div > div > span").click()

        # 步骤12: 点击元素
        await page.locator("span > span:nth-of-type(2) > span > svg > path:nth-of-type(1)").click()

        # 步骤13: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤14: 输入文本
        await page.locator("#form_item_captcha").fill("3980")

        # 步骤15: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div > button > span").click()

        # 步骤16: 点击元素
        await page.locator("#form_item_password").click()

        # 步骤17: 输入文本
        await page.locator("#form_item_password").fill("JS_m258369")

        # 步骤18: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤19: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤20: 输入文本
        await page.locator("#form_item_captcha").fill("3")

        # 步骤21: 输入文本
        await page.locator("#form_item_captcha").fill("3174")

        # 步骤22: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div > div > button").click()

        # 步骤23: 页面导航
        await page.goto("http://192.168.100.167/hxkr/#/dashboard")
        await page.wait_for_load_state("networkidle")

        # 步骤24: 点击元素
        # 目标: 应用中心
        await page.locator("header > div:nth-of-type(2) > ul > li:nth-of-type(2) > span:nth-of-type(2)").click()

        # 步骤25: 页面导航
        await page.goto("http://192.168.100.167/hxkr/#/config/appCenter")
        await page.wait_for_load_state("networkidle")

        # 步骤26: 点击元素
        await page.locator("div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(8) > img").click()

        # 截图保存
        await page.screenshot(path="test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())