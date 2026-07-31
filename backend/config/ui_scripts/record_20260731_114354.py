#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: https://www.baidu.com/?tn=49055317_59_hao_pg
# 生成时间: 2026-07-31 11:43:54
# 操作数量: 3

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
        await page.goto("https://www.baidu.com/?tn=49055317_59_hao_pg")
        await page.wait_for_load_state("networkidle")

        # 步骤1: 点击元素
        # 目标: 👈 复杂问题文心助手回答更优        百度一下
        await page.locator("div#chat-input-main > div:nth-of-type(4) > div:nth-of-type(1) > div:nth-of-type(3)").click()

        # 步骤2: 点击元素
        # 目标: 百度一下
        await page.locator("#chat-submit-button").click()

        # 步骤3: 页面导航
        await page.goto("https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=49055317_59_hao_pg&wd=%E8%8C%85%E5%8F%B0%E6%B2%BB%E7%90%86%E2%80%9C%E7%99%BD%E9%85%92%E6%82%AC%E6%B2%B3%E2%80%9D&fenlei=256&rsv_pq=0xe9b56b14000852ad&rsv_t=1c3bbEC87dkgyQ6UMd%2FiW4XXG8G2yd6geCcj6AOXjgUlLNp3oLjrHD3A04OM&rqlang=en&rsv_enter=1&rsv_dl=ikrec_click_iph_igh_notyyc_gsnd&rsv_sug3=1&rsv_btype=i&rsv_sug9=eb_1")
        await page.wait_for_load_state("networkidle")

        # 截图保存
        await page.screenshot(path="test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())