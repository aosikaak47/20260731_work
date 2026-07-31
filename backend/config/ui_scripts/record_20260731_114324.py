#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: https://www.baidu.com/?tn=49055317_59_hao_pg
# 生成时间: 2026-07-31 11:43:24
# 操作数量: 14

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
        # 目标: 百度一下
        await page.locator("#chat-submit-button").click()

        # 步骤2: 点击元素
        # 目标: 百度一下
        await page.locator("#chat-submit-button").click()

        # 步骤3: 页面导航
        await page.goto("https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=%E9%87%8D%E5%BA%86%E5%85%A5%E5%A2%83%E6%B8%B8%E7%83%AD%E5%BA%A6%E6%94%80%E5%8D%87&fenlei=256&rsv_pq=0x8c225a070004ea71&rsv_t=ce52SH0tmt5RZwTF0EKlvV3zq7bBw0QtLQV8mOKQoPGqqBMVMglHCkTDUbqe&rqlang=en&rsv_enter=1&rsv_dl=ikrec_click_iph_igh_notyyc_gsnd&rsv_btype=i&rsv_sug9=eb_1")
        await page.wait_for_load_state("networkidle")

        # 步骤4: 点击元素
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div > div:nth-of-type(2)").click()

        # 步骤5: 点击元素
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div > div:nth-of-type(2)").click()

        # 步骤6: 点击元素
        # 目标: 拖动左侧滑块使图片为正
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div").click()

        # 步骤7: 点击元素
        # 目标: 拖动左侧滑块使图片为正
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div").click()

        # 步骤8: 点击元素
        # 目标: 拖动左侧滑块使图片为正
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div").click()

        # 步骤9: 点击元素
        # 目标: 拖动左侧滑块使图片为正
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div").click()

        # 步骤10: 点击元素
        # 目标: 拖动左侧滑块使图片为正
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div").click()

        # 步骤11: 点击元素
        # 目标: 拖动左侧滑块使图片为正
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div").click()

        # 步骤12: 点击元素
        # 目标: 拖动左侧滑块使图片为正
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div > p").click()

        # 步骤13: 点击元素
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div > div:nth-of-type(2)").click()

        # 步骤14: 点击元素
        await page.locator("div#spin-0 > div:nth-of-type(2) > div:nth-of-type(2) > div > div:nth-of-type(2)").click()

        # 截图保存
        await page.screenshot(path="test_result.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_录制场景())