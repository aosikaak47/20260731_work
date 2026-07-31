#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json
import sys
import os

record_file = 'e:\\trae_work\\autoProject\\backend\\config\\ui_scripts\\record_e1da9eac-a6b8-4a7c-8e8d-2741be13efa2.json'
target_url = 'https://www.baidu.com'
headless_mode = False

# 录制注入脚本
INJECT_SCRIPT = "\n(function() {\n    window.__recordedActions = [];\n    document.addEventListener('click', function(e) {\n        var action = { type: 'click', selector: 'test' };\n        console.log('__RECORD_ACTION__:' + JSON.stringify(action));\n    }, true);\n})();\n"

def save_actions(actions, status="recording"):
    try:
        data = dict(actions=actions, status=status, count=len(actions))
        with open(record_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print("Save error: %s" % e, flush=True)

async def main():
    try:
        from playwright.async_api import async_playwright
        
        print("[Recorder] Starting browser, url=%s" % target_url, flush=True)
        save_actions([], "starting")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless_mode)
            context = await browser.new_context()
            page = await context.new_page()
            
            print("[Recorder] Browser launched, navigating to %s" % target_url, flush=True)
            
            # 注入录制脚本
            await page.add_init_script(INJECT_SCRIPT)
            
            recorded_actions = []
            
            def on_console(msg):
                try:
                    if msg.text.startswith("__RECORD_ACTION__:"):
                        action_data = msg.text.replace("__RECORD_ACTION__:", "")
                        action = json.loads(action_data)
                        recorded_actions.append(action)
                        save_actions(recorded_actions, "recording")
                        print("[Recorder] Captured action: %s - %s" % (action.get("type", ""), action.get("selector", action.get("url", ""))), flush=True)
                except Exception as e:
                    print("[Recorder] Console error: %s" % e, flush=True)
            
            page.on("console", on_console)
            
            # 导航到目标URL
            await page.goto(target_url, wait_until="domcontentloaded")
            print("[Recorder] Page loaded, waiting for user actions...", flush=True)
            save_actions(recorded_actions, "recording")
            
            # 等待用户操作或浏览器关闭
            try:
                # 定期保存状态
                async def heartbeat():
                    while True:
                        await asyncio.sleep(1)
                        save_actions(recorded_actions, "recording")
                
                heartbeat_task = asyncio.create_task(heartbeat())
                
                # 等待浏览器关闭或超时
                try:
                    await page.wait_for_event("close", timeout=3600000)
                except asyncio.TimeoutError:
                    print("[Recorder] Timeout, closing browser", flush=True)
                
                heartbeat_task.cancel()
                
            except Exception as e:
                print("[Recorder] Wait error: %s" % e, flush=True)
            
            save_actions(recorded_actions, "completed")
            print("[Recorder] Session ended. Total actions: %d" % len(recorded_actions), flush=True)
            await browser.close()
            
    except Exception as e:
        print("[Recorder] Error: %s" % e, flush=True)
        try:
            save_actions([], "error: %s" % e)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
