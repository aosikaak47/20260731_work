#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: http://192.168.100.167/hxkr/#/passport/login
# 生成时间: 2026-07-30 14:32:31
# 操作数量: 1

import asyncio
from playwright.async_api import async_playwright


async def test_录制场景:
    """
    录制场景
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开目标页面
        await page.goto("http://192.168.100.167/hxkr/#/passport/login")
        await page.wait_for_load_state("networkidle")

        # 步骤1: 输入文本
        await page.locator("11").fill("11")

        # 截图保存
        await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260730_143304/test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())