#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: http://192.168.100.167/hxkr/#/config/appCenter
# 生成时间: 2026-07-31 10:53:43
# 操作数量: 32

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

        # 步骤4: 输入文本
        await page.locator("#form_item_username").fill("admin")

        # 步骤5: 点击元素
        await page.locator("#form_item_password").click()

        # 步骤6: 输入文本
        await page.locator("#form_item_password").fill("JS_")

        # 步骤7: 输入文本
        await page.locator("#form_item_password").fill("JS_M258369")

        # 步骤8: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤9: 输入文本
        await page.locator("#form_item_captcha").fill("3276")

        # 步骤10: 点击元素
        await page.locator("div > div > label > span:nth-of-type(1) > input").click()

        # 步骤11: 点击元素
        await page.locator("div > div > label > span:nth-of-type(1) > input").click()

        # 步骤12: 输入文本
        await page.locator("div > div > label > span:nth-of-type(1) > input").fill("on")

        # 步骤13: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div > div > button").click()

        # 步骤14: 点击元素
        await page.locator("div > span > span:nth-of-type(2) > span > svg").click()

        # 步骤15: 点击元素
        await page.locator("#form_item_password").click()

        # 步骤16: 输入文本
        await page.locator("#form_item_password").fill("JS_m258369")

        # 步骤17: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤18: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤19: 输入文本
        await page.locator("#form_item_captcha").fill("93")

        # 步骤20: 输入文本
        await page.locator("#form_item_captcha").fill("9")

        # 步骤21: 输入文本
        await page.locator("#form_item_captcha").fill("9391")

        # 步骤22: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div > div > button").click()

        # 步骤23: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤24: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤25: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤26: 点击元素
        await page.locator("#form_item_captcha").click()

        # 步骤27: 输入文本
        await page.locator("#form_item_captcha").fill("2168")

        # 步骤28: 点击元素
        # 目标: 登 录
        await page.locator("div > div > div > div > button").click()

        # 步骤29: 页面导航
        await page.goto("http://192.168.100.167/hxkr/#/dashboard")
        await page.wait_for_load_state("networkidle")

        # 步骤30: 点击元素
        # 目标: 应用中心
        await page.locator("header > div:nth-of-type(2) > ul > li:nth-of-type(2) > span:nth-of-type(2)").click()

        # 步骤31: 页面导航
        await page.goto("http://192.168.100.167/hxkr/#/config/appCenter")
        await page.wait_for_load_state("networkidle")

        # 步骤32: 点击元素
        await page.locator("div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(8) > img").click()

        # 截图保存
        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_105350/test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())