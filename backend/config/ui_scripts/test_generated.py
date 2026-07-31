#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json
import sys
import os

record_file = r"e:\trae_work\autoProject\backend\config\ui_scripts\record_b465d87e-6bc6-4bb9-a556-ae2ca4ab724d.json"
target_url = r"https://www.baidu.com"
headless_mode = False

# 录制注入脚本
INJECT_SCRIPT = '\n(function() {\n    window.__recordedActions = [];\n    window.__recordActive = true;\n\n    function getElementSelector(element) {\n        if (element.id) return \'#\' + element.id;\n        if (element.name) return element.tagName.toLowerCase() + \'[name="\' + element.name + \'"]\';\n        var path = [];\n        var current = element;\n        while (current && current.nodeType === 1 && path.length < 5) {\n            var selector = current.tagName.toLowerCase();\n            if (current.id) { selector += \'#\' + current.id; path.unshift(selector); break; }\n            var parent = current.parentNode;\n            if (parent) {\n                var siblings = Array.from(parent.children).filter(function(c) { return c.tagName === current.tagName; });\n                if (siblings.length > 1) {\n                    var index = siblings.indexOf(current) + 1;\n                    selector += \':nth-of-type(\' + index + \')\';\n                }\n                path.unshift(selector);\n            }\n            current = current.parentNode;\n        }\n        return path.join(\' > \');\n    }\n\n    function sendAction(action) {\n        action.timestamp = Date.now();\n        window.__recordedActions.push(action);\n        console.log(\'__RECORD_ACTION__:\' + JSON.stringify(action));\n    }\n\n    document.addEventListener(\'click\', function(e) {\n        if (!window.__recordActive) return;\n        var action = { type: \'click\', selector: \'test\', elementType: \'button\', text: \'Click Me\', tagName: \'button\' };\n        sendAction(action);\n    }, true);\n\n    console.log(\'[UI Recorder] Recording started.\');\n})();\n'

def save_actions(actions, status="recording"):
    try:
        data = {"actions": actions, "status": status, "count": len(actions)}
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Save error: {e}", flush=True)

async def main():
    try:
        from playwright.async_api import async_playwright
        
        print(f"[Recorder] Starting browser, url={target_url}", flush=True)
        save_actions([], "starting")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless_mode)
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"[Recorder] Browser launched, navigating to {target_url}", flush=True)
            
            # 注入录制脚本
            await page.add_init_script(INJECT_SCRIPT)
            
            recorded_actions = []
            
            def on_console(msg):
                try:
                    if msg.text.startswith('__RECORD_ACTION__:'):
                        action_data = msg.text.replace('__RECORD_ACTION__:', '')
                        action = json.loads(action_data)
                        recorded_actions.append(action)
                        save_actions(recorded_actions, "recording")
                        print(f"[Recorder] Captured action: {action.get('type', '')} - {action.get('selector', action.get('url', ''))}", flush=True)
                except Exception as e:
                    print(f"[Recorder] Console error: {e}", flush=True)
            
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
                print(f"[Recorder] Wait error: {e}", flush=True)
            
            save_actions(recorded_actions, "completed")
            print(f"[Recorder] Session ended. Total actions: {len(recorded_actions)}", flush=True)
            await browser.close()
            
    except Exception as e:
        print(f"[Recorder] Error: {e}", flush=True)
        try:
            save_actions([], f"error: {e}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
