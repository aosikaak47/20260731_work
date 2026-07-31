# Playwright 自动化测试脚本 (Python)
# 用例名称: 登录
# 生成时间: 2026-07-31 11:35:51

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

SCRIPT_DIR = 'E:\\trae_work\\autoProject\\backend\\app\\../config/ui_results'
SESSION_ID = '41491197-c3c6-4943-9a69-e542ed3de5fc'

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
            await page.goto("http://192.168.100.167/hxkr/#/passport/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(STEP_DELAY)

            await page.screenshot(path="E:\trae_work\autoProject\backend\app\../config/ui_results\result_20260731_113614/test_result.png")
            await browser.close()
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_test())