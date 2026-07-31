# Playwright 自动化测试脚本 (Python)
# 用例名称: 登录功能测试
# 生成时间: 2026-07-31 14:26:06

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

# 配置
SLOW_MO = 500  # 操作间隔(ms)，模拟人类操作速度
STEP_DELAY = 800  # 步骤间延迟(ms)
HEADLESS = False  # 是否无头模式
CAPTCHA_PAUSE_FILE = None  # 验证码暂停文件路径

SCRIPT_DIR = 'E:\\trae_work\\autoProject\\backend\\config\\ui_results'
SESSION_ID = 'd7eadfd5-4818-4e5b-b5a6-4f02b706d8f8'

async def wait_for_captcha_input():
    """等待用户手动输入验证码"""
    captcha_file = os.path.join(SCRIPT_DIR, f"captcha_input_{SESSION_ID}.json")
    pause_file = os.path.join(SCRIPT_DIR, f"captcha_pause_{SESSION_ID}.json")
    
    # 通知前端已暂停等待验证码
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    with open(pause_file, "w", encoding="utf-8") as f:
        json.dump({"status": "paused", "message": "等待验证码输入"}, f)
    print("[Captcha] 已暂停，等待用户输入验证码...", flush=True)
    
    # 轮询等待用户输入验证码
    while True:
        await asyncio.sleep(1)
        if os.path.exists(captcha_file):
            try:
                with open(captcha_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                captcha_code = data.get("code", "")
                if captcha_code:
                    print(f"[Captcha] 收到验证码: {captcha_code}", flush=True)
                    # 清理文件
                    os.remove(captcha_file)
                    os.remove(pause_file)
                    return captcha_code
            except Exception as e:
                print(f"[Captcha] 读取验证码出错: {e}", flush=True)
                continue
    
async def run_test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            # 打开目标页面
            await page.goto("http://localhost:5173/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(STEP_DELAY)

            # 打开登录页
            await page.goto("http://localhost:5173/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(STEP_DELAY)

            # 输入用户名
            input_value = "admin"
            input_done = False
            for loc_expr in [
                lambda: page.locator("//input[@name='username']"),
                lambda: page.get_by_role("textbox", name="用户名输入框"),
                lambda: page.get_by_placeholder("用户名输入框"),
                lambda: page.locator("input").first
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill(input_value)
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("input").first.fill(input_value, force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 输入密码
            input_value = "123456"
            input_done = False
            for loc_expr in [
                lambda: page.locator("//input[@name='password']"),
                lambda: page.get_by_role("textbox", name="密码输入框"),
                lambda: page.get_by_placeholder("密码输入框"),
                lambda: page.locator("input").first
            ]:
                try:
                    locator = loc_expr()
                    await locator.wait_for(state="visible", timeout=5000)
                    await locator.fill(input_value)
                    input_done = True
                    break
                except Exception:
                    continue
            if not input_done:
                await page.locator("input").first.fill(input_value, force=True)
            await page.wait_for_timeout(STEP_DELAY)

            # 点击登录
            click_done = False
            for loc_expr in [
                lambda: page.locator("button.login-btn"),
                lambda: page.get_by_text("登录按钮"),
                lambda: page.get_by_role("button", name="登录按钮"),
                lambda: page.get_by_role("link", name="登录按钮"),
                lambda: page.locator("button").first
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
                raise Exception("Failed to click: 登录按钮")
            await page.wait_for_timeout(STEP_DELAY)

            # 验证登录成功
            try:
                await page.get_by_text("首页工作台").first.wait_for(state="visible", timeout=10000)
                print("断言成功: 找到文本 \"首页工作台\"")
            except Exception as e:
                print(f"断言失败: {e}")
            await page.wait_for_timeout(STEP_DELAY)

            await page.screenshot(path="E:/trae_work/autoProject/backend/config/ui_results/result_20260731_142607/test_result.png")
            await browser.close()
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_test())