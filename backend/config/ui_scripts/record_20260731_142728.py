#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playwright 自动化测试脚本
# 用例名称: 录制场景
# 目标URL: http://192.168.100.167/hxkr/#/config/appCenter
# 生成时间: 2026-07-31 14:27:28
# 操作数量: 14

import asyncio
from playwright.async_api import async_playwright

# 配置
SLOW_MO = 500  # 操作间隔(ms)，模拟人类操作速度
STEP_DELAY = 800  # 步骤间延迟(ms)
HEADLESS = False  # 是否无头模式


async def test_录制场景():
    """
    录制场景
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            # 打开目标页面
            await page.goto("http://192.168.100.167/hxkr/#/config/appCenter", wait_until="domcontentloaded")
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤1: 页面导航
            await page.goto("http://192.168.100.167/hxkr/#/passport/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤2: 点击元素
            click_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_username"),
                lambda: page.get_by_text(""),
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
                await page.locator("#form_item_username").click(force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤3: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_username"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("admin")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("#form_item_username").fill("admin", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤4: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_username"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("admin")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("#form_item_username").fill("admin", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤5: 点击元素
            click_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_password"),
                lambda: page.get_by_text(""),
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
                await page.locator("#form_item_password").click(force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤6: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_password"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("JS")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("#form_item_password").fill("JS", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤7: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_password"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("JS_")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("#form_item_password").fill("JS_", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤8: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_password"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("JS_m")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("#form_item_password").fill("JS_m", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤9: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_password"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("JS_m258369")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("#form_item_password").fill("JS_m258369", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤10: 点击元素
            click_done = False
            for loc_expr in [
                lambda: page.locator("#form_item_captcha"),
                lambda: page.get_by_text(""),
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
                await page.locator("#form_item_captcha").click(force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤11: 点击元素
            # 目标: 记住密码
            click_done = False
            for loc_expr in [
                lambda: page.locator("div > div > div > label > span:nth-of-type(2)"),
                lambda: page.get_by_text("记住密码"),
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
                await page.locator("div > div > div > label > span:nth-of-type(2)").click(force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤12: 点击元素
            click_done = False
            for loc_expr in [
                lambda: page.locator("div > div > label > span:nth-of-type(1) > input"),
                lambda: page.get_by_text(""),
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
                await page.locator("div > div > label > span:nth-of-type(1) > input").click(force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤13: 输入文本
            input_done = False
            for loc_expr in [
                lambda: page.locator("div > div > label > span:nth-of-type(1) > input"),
                lambda: page.get_by_role("textbox"),
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill("on")
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("div > div > label > span:nth-of-type(1) > input").fill("on", force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 步骤14: 点击元素
            # 目标: 登 录
            click_done = False
            for loc_expr in [
                lambda: page.locator("div > div > div > div > button"),
                lambda: page.get_by_text("登 录"),
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
                await page.locator("div > div > div > div > button").click(force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 截图保存
            await page.screenshot(path="test_result.png")
            await browser.close()
            print("✓ 测试执行完成")
    except Exception as e:
        print(f"✗ 测试执行失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_录制场景())